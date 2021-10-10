import os,sys,json,hashlib,time,demjson

def sync_users_file(data):
    print(data)
    with open("config/users.json",'w+') as file:
        file.write(json.dumps(data))

def get_user_item(username:str):
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())
    #print(data)
    return data.get(username)

def check_user(username:str,password:str):
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())
    password = '_@zqhf_oj_password_enFoZi1vai1wYXNzd29yZC1wcmVmaXg=' + password
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    if data.get(username)["password"] == password:
        return True
    else:
        return False

def set_user_premission(username:str,level:int):
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())
    data[username]["premission"] = level
    sync_users_file(data)

def set_user_password(username:str,password:str):
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())
    password = '_@zqhf_oj_password_enFoZi1vai1wYXNzd29yZC1wcmVmaXg=' + password
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    data[username]["password"] = password
    sync_users_file(data)

def set_user_descriptions(username:str, desciptions:dict):
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())
    data[username]["descriptions"] = desciptions
    sync_users_file(data)

def get_user_descriptions(username:str):
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())
    return data[username]["descriptions"]

def new_user(username:str,level:int,pwd:str):
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())
    data[username] = {}
    sync_users_file(data)
    set_user_premission(username,level)
    set_user_password(username,pwd)
    set_user_descriptions( username, 
    {
        'description':'👴莫得介绍', 
        'user-img':'',
        'join-time':time.strftime('%Y-%m-%d %H:%M:%S UTC' + str(time.timezone),time.localtime(time.time())),
        'introduction': '',
        'solved-problems': []
    })

def remove_user(username:str):
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())
    if data.get(username) == None:
        return 0
    else:
        del data[username]
        sync_users_file(data)
        return 1
