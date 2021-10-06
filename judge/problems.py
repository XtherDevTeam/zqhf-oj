import os,sys,json,urllib.parse

data = []

def sync_problems_file():
    with open('judge/problem_list.json','w+') as file:
        file.write( json.dumps({ 'description':'题库' , 'problem_list': data}) )

def open_problems_file():
    temp = None
    with open('judge/problem_list.json','r+') as file:
        temp = json.loads(file.read())['problem_list']
    global data
    data = temp

def get_problem(pid:int):
    if pid >= len(data):
        return None
    else: return data[pid]

def get_judge_file(pid:int):
    if pid >= len(data):
        return None
    else:
        pid = str(pid)
        result = []
        with open('judge/judge_files/' + pid + '.in','r+') as file:
            result.append(urllib.parse.quote(file.read()))
        with open('judge/judge_files/' + pid + '.out','r+') as file:
            result.append(urllib.parse.quote(file.read()))
        return result

def edit_problem(pid:int,problem_infomation:dict):
    data[pid] = problem_infomation
    sync_problems_file()

def new_problem(problem_infomation:dict):
    data.append(problem_infomation)
    sync_problems_file()
    return len(data) - 1

def remove_problem(pid:int):
    del data[pid]
    return len(data) - 1

def get_problems_count():
    return len(data)

def get_problems_per_page(prefix:int,count:int):
    result = []
    if prefix > len(data):
        return data
    if count > len(data):
        return data
    for i in range(count):
        if prefix + i > len(data) - 1:
            continue
        result.append(data[prefix + i])
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
    