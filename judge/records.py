import os,sys,json,web.users

def sync_records(data):
    with open('judge/records.json','w+') as file:
        print("syncing records...",data)
        file.write( json.dumps({'description':"记录",'records':data}) )

def get_record(jid:int):
    temp = None
    with open('judge/records.json','r+') as file:
        temp = json.loads(file.read())["records"]
    if jid >= len(temp):
        return None
    return temp[jid]

def get_records():
    temp = None
    with open('judge/records.json','r+') as file:
        temp = json.loads(file.read())["records"]
    return temp

def get_record_count():
    temp = None
    with open('judge/records.json','r+') as file:
        temp = json.loads(file.read())["records"]
    return len(temp)

def push_record(info:list):
    temp = None
    jid = -1
    with open('judge/records.json','r+') as file:
        temp = json.loads(file.read())["records"]
        temp.append(info)
        jid = len(temp) - 1
    sync_records(temp)
    if temp[0][0] == 'Accepted':
        print('AC:' , info[2], info[3])
        description = web.users.get_user_descriptions(info[2])
        if description['solved-problems'].count(int(info[3])) == 0:
            description['solved-problems'].append(int(info[3]))
            web.users.set_user_descriptions(info[2],description)
    return jid

