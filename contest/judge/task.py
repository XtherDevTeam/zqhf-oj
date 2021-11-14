import threading
import os,time
from sys import stdout
import judge.plugins,traceback

problems = None
status = ['']
full_stdout = ['']
status_queue_prefix = 0
queue = []

def push_task(use_plugin:str,input:str,output:str,source:str,binary:str,author:str,pid:int):
    queue.append( [ use_plugin, input, source, binary, output,author,int(pid) ] )
    print('task pushed->',[ use_plugin, input, source, binary, output,author,int(pid) ])
    return judge.records.get_record_count()

def task_processor():
    # judge.plugins.load_plugins_list()
    while True:
        try:
            global status_queue_prefix
            while len(queue) == 0:
                print('do nothing', end='\b\b\b\b\b\b\b\b\b\b')
                time.sleep(0.1)
                continue
            now_item = queue[-1]
            queue.pop()
            status[status_queue_prefix] = 'compiling'
            problem_details = judge.problems.get_problem(now_item[6])
            if problem_details == None:
                print('invalid problem!', type(now_item[6]))
                continue
            print('time-limit:' , problem_details['time_limit'], 'memory-limit:', problem_details['mem_limit'])
            execute_result = judge.plugins.execute_plugin(
                now_item[0],
                now_item[1],
                { 'source_file':now_item[2],'binary_file':now_item[3] },
                problem_details['time_limit'],
                problem_details['mem_limit']
            )
            try:
                os.remove('./tmp/' + now_item[2])
                os.remove('./tmp/' + now_item[3])
            except Exception:
                pass
            if execute_result[0] == 'CE':
                status[status_queue_prefix] = 'Compile Error'
            elif execute_result[0] == 'RE':
                status[status_queue_prefix] = 'Runtime Error'
            elif execute_result[0] == 'TLE':
                status[status_queue_prefix] = 'Time Limit Exceeded'
            else:
                # 去除末尾多余字符
                if execute_result[1] != "":
                    print("not empty result:",execute_result)
                    while execute_result[1][-1] == '\n' or execute_result[1][-1] == ' ':
                        execute_result[1] = execute_result[1][0:-1]
                if now_item[4] != "":
                    while now_item[4][-1] == '\n' or now_item[4][-1] == ' ':
                        now_item[4] = now_item[4][0:-1]
                if len(execute_result[1]) != len(now_item[4]):
                    # print(execute_result[1],'\n',now_item[4])
                    status[status_queue_prefix] = 'Wrong Answer at character ' + str(len(execute_result[1])) + ' of ' + str(len(now_item[4]))
                else:
                    for i in range(len(now_item[4])-1):
                        if(execute_result[1][i] != now_item[4][i]):
                            status[status_queue_prefix] = 'Wrong Answer at character ' + str(i)
                            break
                if status[status_queue_prefix] == 'compiling': status[status_queue_prefix] = 'Accepted'
            full_stdout[status_queue_prefix] = 'stdout >\n' + execute_result[1] + '\n\nstderr >\n' + execute_result[2] + '\n\n' + 'returncode >\n' + str(execute_result[3]) + '\n'
            # print(execute_result)
        except Exception as e:
            traceback.print_exc()
            pass
    print('unexpected exit')

def init():
    global tasks
    judge.plugins.load_plugins_list()
    process = threading.Thread(target=task_processor)
    process.start()
    print('judge task runner started')
