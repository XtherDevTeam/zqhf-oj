import os,sys,json,web.users,config.global_config,database.client,web.ranking
'''
def sync_records(data):
    with open('judge/records.json','w+') as file:
        print("syncing records...",data)
        file.write( json.dumps({'description':"记录",'records':data}) )
'''
def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))

def get_record(jid:int):
    result = database.client.table_operate('oj_records','info')
    if result[0] == 'FAIL': return None
    if jid >= result[1]['total_data_cnt']:
        return None
    return database.client.item_operate('oj_records',jid,'get')[1]

def get_records_per_page(prefix:int):
    query_info = database.client.table_operate('oj_records','info')
    print(query_info)
    result = []
    for i in range(query_info[1]['total_data_cnt'] - prefix - 10,query_info[1]['total_data_cnt']):
        if i < 0: continue
        if i == query_info[1]['total_data_cnt']: break
        temp = get_record(i)
        temp = [temp, {
            'record_id': i,
        }]
        result.append(temp)
    result.reverse()
    return result

def get_record_count():
    query_info = database.client.table_operate('oj_records','info')
    return query_info[1]['total_data_cnt']

def push_record(info:list):
    temp = info
    jid = get_record_count()
    database.client.item_operate('oj_records',jid,'new',info)
    print(info)
    if temp[0] == 'Accepted':
        print('AC:' , info[2], info[3])
        description = web.users.get_user_descriptions(info[2])
        if description['solved-problems'].count(int(info[3])) == 0:
            description['solved-problems'].append(int(info[3]))
            web.users.set_user_descriptions(info[2],description)
            web.ranking.init_ranking_table()
    return jid

init()