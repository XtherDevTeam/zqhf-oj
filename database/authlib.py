import json,os,hashlib

def initUserInfomation():
    with open('database/auth.json','w+') as file:
        file.write(json.dumps({ 'description':'database users infomation','data':{} }))

def getUserInfomation():
    with open('database/auth.json','r+') as file:
        return json.loads(file.read())['data']

def dumpUserInfomation(data:dict):
    with open('database/auth.json','w+') as file: file.write(json.dumps({ 'description':'database users infomation','data':data }))

def checkUserInfomation(username:str,password:str):
    info = getUserInfomation()
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    if info.get(username) == None or info.get(username) != password: return False
    else: return True