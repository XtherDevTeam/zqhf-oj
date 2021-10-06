import os,sys,json

def sync_records(data):
    with open('judge/records.json','w+') as file:
        file.write( json.dumps({'description':"记录",'records':data}) )

def get_record(jid:int):
    temp = None
    with open('judge/records.json','r+') as file:
        temp = json.loads(file.read())["records"]
    if jid >= len(temp):
        return None
    return temp[jid]

def push_record(info:list):
    temp = None
    jid = -1
    with open('judge/records.json','r+') as file:
        temp = json.loads(file.read())["records"]
        temp.append(info)
        jid = len(temp) - 1
    sync_records(temp)
    return jid

