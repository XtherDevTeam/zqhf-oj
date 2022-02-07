import database.client,config.global_config

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))

def get_lists_count():
    data = database.client.table_operate('oj_problem_lists','info')
    if data[0] == 'FAIL': return 0
    return data[1]['total_data_cnt']

def get_problem_list(name:str):
    data = database.client.item_operate('oj_problem_lists',name,'get')
    if data[0] == 'FAIL': return None
    return data[1]

def get_problem_list_names():
    data = database.client.table_operate('oj_problem_lists','all')
    if data[0] == 'FAIL': return None
    return data[1]['data']

def id_to_name(id:int):
    query_result = get_problem_list_names()
    if query_result == None: return None
    if id >= len(query_result): return None
    return query_result[id]

def get_problem_lists_per_page(prefix:int):
    query_result = get_problem_list_names()
    if query_result == None: return []
    end = prefix + 10
    if prefix >= len(query_result): prefix = len(query_result) - 1
    if prefix < 0: prefix = 0
    if end >= len(query_result): end = len(query_result)

    result = []

    for i in range(prefix,end):
        query = get_problem_list(id_to_name(i))
        if query == None: break
        result.append( [i,query] )
    return result

def new_problem_list(name:str,author:str,description:str,content:list):
    return database.client.item_operate('oj_problem_lists',name,'new',{
        'name':name,
        'author':author,
        'content': content,
        'description': description
    })

def remove_problem_list(name:str):
    return database.client.item_operate('oj_problem_lists',name,'delete')

init()