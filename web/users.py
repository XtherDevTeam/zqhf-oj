import os,sys,json,hashlib

data = {}

def open_users_file():
    with open("config/users.json",'r+') as file:
        data = json.loads(file.read())

def sync_users_file():
    with open("config/users.json",'r+') as file:
        file.write(json.dumps(data))

def get_user_item(username:str):
    return data[username]

def set_user_premission(username:str,level:int):
    data[username]["premissionn"] = level
    sync_users_file()

def set_user_password(username:str,password:str):
    password = '_@zqhf_oj_password_enFoZi1vai1wYXNzd29yZC1wcmVmaXg=' + password
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    data[username]["password"] = password
    sync_users_file()

def new_user(username:str,level:int,pwd:str):
    set_user_premission(username,level)
    set_user_password(username,pwd)

def remove_user(username:str):
    if data.get(username) == None:
        return 0
    else:
        del data[username]
        return 1
