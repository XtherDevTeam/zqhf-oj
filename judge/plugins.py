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
    
def execute_plugin( use_plugin:str, input:str, env:dict, time_out:int = 1000):
    fork = plugins_list[origin_list.index(use_plugin)]
    for i in env:
        print(fork)
        fork['exec_command'] = fork['exec_command'].replace('$'+i,env[i])
    ret_stdout = ''
    ret_stderr = ''
    
    stat = ''
    fp = Popen(fork['exec_command'],shell=True,cwd=os.getcwd() + '/tmp',stdin=PIPE,stdout=PIPE,stderr=PIPE)
    fp.stdin.write(input.encode('utf-8'))
    time.sleep(time_out / 1000)
    fp.poll()
    fp.kill()
    if fp.returncode == None: stat = 'TLE'
    elif fp.returncode != 0: stat = 'ERR'
    else: stat = 'OK'
    ret_stdout += fp.stdout.read().decode('utf-8')
    ret_stderr += fp.stderr.read().decode('utf-8')
    fp.stdout.flush()
    return [stat, ret_stdout, ret_stderr]
    