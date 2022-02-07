import database.client,config.global_config,time,urllib.parse,base64,sys

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))
  
def get_images_count(username:str):
    query_result = database.client.table_operate('oj_userimage_' + username, 'info')
    if query_result[0] != 'OK':
        database.client.table_operate('oj_userimage_' + username + "@list", 'new')
        query_result = database.client.table_operate('oj_userimage_' + username, 'info')
        return query_result[1]['total_data_cnt']
    return query_result[1]['total_data_cnt']
    
def new_image(username:str,userimg:bytes):
    database.client.item_operate('oj_userimage_' + username, get_images_count(username),'new', userimg)
    return
    
def remove_image(username:str,index:int):
    database.client.item_operate('oj_userimage_' + username, index, 'delete')
    return
    
def get_image(username:str,index:int):
    data = database.client.item_operate('oj_userimage_' + username, index,'get')

    if data[0] != 'OK':
        return data
        
    return data[1]

init()