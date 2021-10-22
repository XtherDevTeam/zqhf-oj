import os,sys,json,hashlib,time,demjson,database.client,config.global_config,web.ranking


def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))

def get_user_item(username:str):
    result = database.client.item_operate('oj_users',username,'get')
    if result[0] == 'FAIL': return None
    return result[1]

def check_user(username:str,password:str):
    info = get_user_item(username)
    password = '_@zqhf_oj_password_enFoZi1vai1wYXNzd29yZC1wcmVmaXg=' + password
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    if info["password"] == password:
        return True
    else:
        return False

def set_user_premission(username:str,level:int):
    info = get_user_item(username)
    info["premission"] = level
    database.client.item_operate('oj_users',username,'change',info)

def set_user_password(username:str,password:str):
    info = get_user_item(username)
    password = '_@zqhf_oj_password_enFoZi1vai1wYXNzd29yZC1wcmVmaXg=' + password
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    info["password"] = password
    database.client.item_operate('oj_users',username,'change',info)

def set_user_descriptions(username:str, desciptions:dict):
    result = get_user_item(username)
    result["descriptions"] = desciptions
    database.client.item_operate('oj_users',username,'change',result)

def get_user_descriptions(username:str):
    return get_user_item(username)["descriptions"]

def new_user(username:str,level:int,pwd:str):
    info = {}
    database.client.item_operate('oj_users',username,'new',info)
    set_user_premission(username,level)
    set_user_password(username,pwd)
    set_user_descriptions( username, 
    {
        'description':'👴莫得介绍', 
        'user-img':'',
        'join-time':time.strftime('%Y-%m-%d %H:%M:%S UTC' + str(time.timezone/60/60),time.localtime(time.time() + time.timezone)),
        'introduction': '',
        'solved-problems': []
    })
    web.ranking.init_ranking_table()


def remove_user(username:str):
    database.client.item_operate('oj_users',username,'delete')

init()