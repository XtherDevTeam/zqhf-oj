import os,sys,json,urllib.parse,database.client,config.global_config,markdown

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))

def get_problem(pid:int):
    data = database.client.item_operate('oj_problems',pid,'get')
    if data[0]== 'FAIL': return None
    try:
        data[1]['description-html'] = markdown.markdown(urllib.parse.unquote(data[1]['description']),extensions=[
            'markdown_katex'
        ],extension_configs={
            'markdown_katex': {
                'no_inline_svg': True,
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
        result = []
        with open('judge/judge_files/' + pid + '.in','r+') as file:
            result.append(urllib.parse.quote(file.read()))
        with open('judge/judge_files/' + pid + '.out','r+') as file:
            result.append(urllib.parse.quote(file.read()))
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
    cnt = get_problems_count()
    os.remove('judge/judge_files/' + str(pid) + '.in')
    os.remove('judge/judge_files/' + str(pid) + '.out')
    for i in range(pid+1,cnt):
        if i == cnt - 1: 
            database.client.item_operate('oj_problems',i,'delete')
            break
        data = get_problem(i)
        edit_problem(i-1,data)
        os.rename('judge/judge_files/' + str(i) + '.in','judge/judge_files/' + str(i-1) + '.in')
        os.rename('judge/judge_files/' + str(i) + '.out','judge/judge_files/' + str(i-1) + '.out')

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
    pid = str(pid)
    with open('judge/judge_files/' + pid + '.in','w+') as file:
        file.write(input)
    with open('judge/judge_files/' + pid + '.out','w+') as file:
        file.write(output)
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

init()