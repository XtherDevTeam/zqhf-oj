import os,sys,web.config,json,time
from subprocess import Popen, PIPE, STDOUT

plugins_list = []
origin_list = []

def load_plugins_list():
    global origin_list
    global plugins_list
    web.config.open_config_file()
    origin_list = web.config.get_config_value('use-judge-plugins')
    for i in origin_list:
        with open('judge/plugins/' + i + '.json','r+') as file:
            plugins_list.append(json.loads(file.read()))
    
def execute_plugin( use_plugin:str, input:str, env:dict, time_out:int = 1000, memlimit:int = 1024):
    if len(plugins_list) == 0:
        load_plugins_list()
    fork = plugins_list[origin_list.index(use_plugin)]
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
    fp = Popen('ulimit -m ' + str(memlimit) + ';' + fork['exec_command'],shell=True,cwd=os.getcwd() + '/tmp',stdin=pipe_stdin.fileno(),stdout=pipe_stdout.fileno(),stderr=pipe_stderr.fileno())
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
    print('finish task with output ', ret_stdout)
    return [stat, ret_stdout, ret_stderr, fp.returncode]
    