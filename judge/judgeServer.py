import flask, json, judge.config, requests, io, pickle,os,sys,time
from subprocess import Popen, PIPE, STDOUT

app = flask.Flask(__name__)

def getPluginDetails(name:str):
    with open(judge.config.plugins_dir + '/' + name + '.json', 'r+') as file:
        return json.loads(file.read())


def execute_plugin( use_plugin:str, input:str, env:dict, time_out:int = 1000, memlimit:int = 1024):
    fork = getPluginDetails(use_plugin)
    for i in env:
        fork['compile_command'] = fork['compile_command'].replace('$'+i,env[i])
    for i in env:
        fork['exec_command'] = fork['exec_command'].replace('$'+i,env[i])
    ret_stdout = ''
    ret_stderr = ''
    
    stat = ''
    fp = Popen(fork['compile_command'],shell=True,cwd=os.getcwd() + '/tmp',stdin=PIPE,stdout=PIPE,stderr=PIPE)
    fp.stdout.flush()
    fp.stderr.flush()
    print('waiting for compile')
    fp.wait()
    print('compile success')
    if fp.returncode != 0:
        stat = 'CE'
        print(fp.returncode)
        ret_stdout += fp.stdout.read().decode('utf-8')
        ret_stderr += fp.stderr.read().decode('utf-8')
        fp.stdout.flush()
        return [stat, ret_stdout, ret_stderr,fp.returncode]
    print('waiting for execute: '+ str(time_out) + 'ms')
    with open('./tmp/stdin.log','w+') as file:
        file.write(input)
    pipe_stdin = open('./tmp/stdin.log','r+')
    pipe_stdout = open('./tmp/stdout.log','w+')
    pipe_stderr = open('./tmp/stderr.log','w+')
    print('executing: ',fork['compile_command'],fork['exec_command'], 'memlimit', memlimit)
    fp = Popen('ulimit -m ' + str(memlimit) + ';ulimit -v ' + str(memlimit) + ';' + fork['exec_command'],shell=True,cwd=os.getcwd() + '/tmp',stdin=pipe_stdin.fileno(),stdout=pipe_stdout.fileno(),stderr=pipe_stderr.fileno())
    time.sleep(time_out / 1000)
    fp.poll()
    fp.kill()
    print('task killed')
    if fp.returncode == None: stat = 'TLE'
    else: stat = 'OK'
    pipe_stdout.seek(0)
    pipe_stderr.seek(0)
    ret_stdout += pipe_stdout.read()
    ret_stderr += pipe_stderr.read()
    pipe_stderr.close()
    pipe_stdout.close()
    pipe_stdin.close()
    # print('finish task with output ', ret_stdout)
    return [stat, ret_stdout, ret_stderr, fp.returncode]

def checker(result, expectedOutput):
    if(result['status'] == 'CE'):
        result['status'] = 'Compile Error'
        return result
    elif(result['return_code'] == None or result['return_code'] != '0'):
        result['status'] = 'Runtime Error'
        return result
    
    if result['stdout'] != "":
        while result['stdout'][-1] == '\n' or result['stdout'][-1] == ' ':
            result['stdout'] = result['stdout'][0:-1]
            
    if expectedOutput != "":
        while expectedOutput[-1] == '\n' or expectedOutput[-1] == ' ':
            expectedOutput = expectedOutput[0:-1]

    if len(result['stdout']) != len(expectedOutput):
        # print(execute_result[1],'\n',now_item[4])
        result['status'] = 'Wrong Answer at character ' + str(len(result['stdout'])) + ' of ' + str(len(expectedOutput))
        return result
        
    else:
        for i in range(len(expectedOutput)-1):
            if(result['stdout'][i] != expectedOutput[i]):
                result['status'] = 'Wrong Answer at character ' + str(i)
                return result
            
    result['status'] = 'Accepted'
    # print(result)
    return result

@app.route('/submit')
def submit_judge():
    
    pickleData = io.BytesIO(bytes())
    flask.request.files.get('data').save(pickleData)
    pickleData.seek(0)
    data = pickle.loads(pickleData.read())
    pickleData.close()
    result_data = execute_plugin(data['plugin'], data['input'], data['env_variables'], data['time_limit'], data['mem_limit'])
    return checker({
        'status': result_data[0],
        'stdout': str(result_data[1]),
        'stderr': str(result_data[2]),
        'return_code': str(result_data[3])
    }, data['output'])

app.run(host = judge.config.host, port = judge.config.port, debug=False )