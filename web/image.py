import database.client,config.global_config,time,urllib.parse,base64

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))
    
def new_image(username:str,userimg:bytes):
    data = database.client.item_operate('oj_userimage',username,'get')
    # d = base64.encodebytes(userimg)
    if data[0] == 'FAIL': database.client.item_operate('oj_userimage',username,'new',[])
    data = data[1]
    data.append(userimg)
    database.client.item_operate('oj_userimage',username,'change', data)
    return
    
def remove_image(username:str,index:int):
    data = database.client.item_operate('oj_userimage',username,'get')
    if data[0] == 'FAIL': database.client.item_operate('oj_userimage',username,'new',[])
    data = data[1]
    if index >= len(data):
        return False
    del data[index]
    database.client.item_operate('oj_userimage',username,'change', data)
    return
    
def get_all_image(username:str):
    data = database.client.item_operate('oj_userimage',username,'get')
    if data[0] == 'FAIL': database.client.item_operate('oj_userimage',username,'new',[])
    data = data[1]
    return data
    
def get_image_cnt(username:str):
    data = database.client.item_operate('oj_userimage',username,'get')
    if data[0] == 'FAIL': database.client.item_operate('oj_userimage',username,'new',[])
    data = data[1]
    return len(data)
    
def get_image(username:str,index:int):
    data = database.client.item_operate('oj_userimage',username,'get')
    if data[0] == 'FAIL': database.client.item_operate('oj_userimage',username,'new',[])
    data = data[1]
    if index >= len(data):
        return False
    return data[index]

init()