import multiprocessing as mp
from sys import stdout
import judge.plugins,judge.records

problems = None
status = ['']
full_stdout = ['']
status_queue_prefix = 0
q = mp.Queue()

def push_task(use_plugin:str,input:str,output:str,source:str,binary:str):
    q.put( [ use_plugin, input, source, binary, output ] )
    status.append( 'waiting' )
    full_stdout.append( '' )
    print(q)
    return len(status) - 1

def task_processor(queue:mp.Queue):
    print('start',queue)
    judge.plugins.load_plugins_list()
    while True:
        global status_queue_prefix
        while queue.empty():
            continue
        print('Are you sure?',status_queue_prefix)
        now_item = queue.get()
        status[status_queue_prefix] = 'compiling'
        execute_result = judge.plugins.execute_plugin(now_item[0],now_item[1], { 'source_file':now_item[2],'binary_file':now_item[3] })
        if execute_result[0] == 'ERR':
            status[status_queue_prefix] = 'Compile Error or Runtime Error'
        elif execute_result[0] == 'TLE':
            status[status_queue_prefix] = 'Time Limit Exceed'
        else:
            # 去除末尾多余字符
            while execute_result[1][-1] == '\n' or execute_result[1][-1] == ' ':
                execute_result[1] = execute_result[1][0:-1]
            for i in range(len(now_item[1])):
                if(execute_result[1][i] != now_item[1][i]):
                    status[status_queue_prefix] = 'Wrong Answer at character ' + str(i)
                    break
            if status[status_queue_prefix] == 'compiling': status[status_queue_prefix] = 'Accepted'
        full_stdout[status_queue_prefix] = 'stdout >\n' + execute_result[1] + '\n\nstderr >\n' + execute_result[2] + '\n'
        judge.records.push_record( [status[0],full_stdout[0]] )
        print(execute_result)
    print('unexpected exit')

def init():
    global tasks
    judge.plugins.load_plugins_list()
    process = mp.Process(target=task_processor,args=(q,))
    process.start()
    push_task("python3","","Hello,world!","test1.py","")
    print(process,q)