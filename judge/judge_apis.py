import io
import requests, json, pickle

import os,sys,json,urllib.parse,database.client,config.global_config,markdown,web.users,web.ranking

plugins_list = []

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))
    global plugins_list
    plugins_list = []
    origin_list = web.config.get_config_value('use-judge-plugins')
    for i in origin_list:
        with open('judge/plugins/' + i + '.json','r+') as file:
            plugins_list.append(json.loads(file.read()))

def get_problem(pid:int):
    data = database.client.item_operate('oj_problems',pid,'get')
    if data[0]== 'FAIL': return None
    try:
        data[1]['description-html'] = markdown.markdown(urllib.parse.unquote(data[1]['description']),extensions=[
            'markdown_katex',
            'markdown.extensions.extra',
            'markdown.extensions.codehilite'
        ],extension_configs={
            'markdown_katex': {
                'no_inline_svg': False,
                'insert_fonts_css': True,
            },
        })
    except Exception:
        data[1]['description-html'] = ''
    return data[1]

def get_judge_file(pid:int):
    data = database.client.item_operate('oj_problems',pid,'get')
    if data[0]== 'FAIL': return None
    else:
        pid = str(pid)
        c = get_problem(pid)
        result = [c['input'], c['output']]
        return result

def edit_problem(pid:int,problem_infomation:dict):
    return database.client.item_operate('oj_problems',pid,'change',problem_infomation)

def new_problem(problem_infomation:dict):
    infomation = database.client.table_operate('oj_problems','info')
    if infomation[0] == 'FAIL': return None
    result = database.client.item_operate('oj_problems',infomation[1]['total_data_cnt'],'new',problem_infomation)
    if result[0] == 'FAIL': return None
    return infomation[1]['total_data_cnt']

def remove_problem(pid:int):
    database.client.item_operate('oj_problems',pid,'delete')
    infomation = database.client.table_operate('oj_problems','info')

    if infomation[0] == 'FAIL': return None
    return infomation[1]['total_data_cnt'] - 1

def get_problems_count():
    infomation = database.client.table_operate('oj_problems','info')
    if infomation[0] == 'FAIL': return None
    return infomation[1]['total_data_cnt']

def get_problems(from_pid:int,to_pid:int):
    result = []
    for i in range(from_pid,to_pid):
        result.append(get_problem(i))
        if result[-1] == None:
            result.pop()
            continue
    return result

def get_problem_names(from_pid:int,to_pid:int):
    result = []
    for i in range(from_pid,to_pid):
        result.append(get_problem(i))
        if result[-1] == None:
            result.pop()
            continue
        result[-1] = result[-1]['name']
    return result

def get_problems_per_page(prefix:int,count:int):
    infomation = database.client.table_operate('oj_problems','info')
    if infomation[0] == 'FAIL':
        # print('why?',infomation)
        return None
    length = infomation[1]['total_data_cnt']
    result = []
    if prefix > length:
        return get_problems(0,length)
    if count > length:
        return get_problems(0,length)
    for i in range(count):
        if prefix + i > length - 1:
            continue
        result.append(get_problem(prefix + i))
    return result

def createJudgeFile(pid:int,input:str,output:str):
    if pid >= get_problems_count():
        return False
    # pid = str(pid)
    # with open('judge/judge_files/' + pid + '.in','w+') as file:
    #     file.write(input)
    # with open('judge/judge_files/' + pid + '.out','w+') as file:
    #     file.write(output)
    n = get_problem(pid)
    n['input'] = input
    n['output'] = output
    edit_problem(pid, n)
    return True

def get_match_tags_problems(tag:str):
    result = []
    for i in range(0,get_problems_count()):
        query = get_problem(i)
        if query == None: continue
        query['id'] = i
        if query['tags'].count(tag) >= 1:
            result.append(query)
    return result

def get_selected_problems_detail(pids:list):
    result = []
    for i in pids:
        query = get_problem(i)
        if query == None: continue
        query['id'] = i
        result.append(query)
    return result

def get_record(jid:int):
    result = database.client.table_operate('oj_records','info')
    if result[0] == 'FAIL': return None
    if jid >= result[1]['total_data_cnt']:
        return None
    return database.client.item_operate('oj_records',jid,'get')[1]

def get_records_per_page(prefix:int):
    query_info = database.client.table_operate('oj_records','info')
    # print(query_info,prefix,10)
    result = []
    for i in range(query_info[1]['total_data_cnt'] - prefix - 10,query_info[1]['total_data_cnt'] - prefix):
        if i < 0: continue
        if i == query_info[1]['total_data_cnt']: break
        temp = get_record(i)
        temp = [temp, {
            'record_id': i,
        }]
        result.append(temp)
    result.reverse()
    return result

def get_record_count():
    query_info = database.client.table_operate('oj_records','info')
    # print(query_info)
    return query_info[1]['total_data_cnt']

def create_executing_task_record(info:list):
    jid = get_record_count()
    database.client.item_operate('oj_records',jid,'new',info)
    return jid

def push_record(info:list, jid:int):
    # temp = info
    database.client.item_operate('oj_records',jid,'change',info)
    # print(info)
    if info[0] == 'Accepted':
        print('AC:' , info[2], info[3])
        description = web.users.get_user_descriptions(info[2])
        if description['solved-problems'].count(int(info[3])) == 0:
            description['solved-problems'].append(int(info[3]))
            web.users.set_user_descriptions(info[2],description)
            web.ranking.init_ranking_table()
    return jid

def submit(judgeServerHost, judgeServerPort, judgePlugin, source_file, input, output, time_limit, mem_limit, env_variables, author, pid):
    jid = create_executing_task_record(['Judging', 'Please wait...', author, pid])
    
    packed_data = io.BytesIO(pickle.dumps(
        {
            'plugin': judgePlugin,
            'input': input,
            'output': output,
            'time_limit': time_limit,
            'mem_limit': mem_limit,
            'env_variables': env_variables,
            'source_file': source_file
        }
    ))
    recv_data = json.loads(requests.get("http://%s:%d/submit" % (judgeServerHost, judgeServerPort), files={'data': packed_data}).content)
    push_record(
        [recv_data['status'], 'stdout> <br>' + recv_data['stdout'] + "<br><br>stderr> <br>" + recv_data['stderr'], author, pid],
        jid
    )
    
    return jid

init()