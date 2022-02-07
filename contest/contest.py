import database.client, config.global_config

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))
    
def getContestsCount():
    infomation = database.client.table_operate('oj_contests','info')
    if infomation[0] == 'FAIL': return None
    return infomation[1]['total_data_cnt']
    
def createContestShell(title:str, description:str, startTime:int, endTime:int):
    database.client.item_operate('oj_contests', getContestsCount(), 'new', {
        'title': title,
        'description': description,
        
    })
    
init()