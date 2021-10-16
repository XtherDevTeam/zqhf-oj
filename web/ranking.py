import database.client,config.global_config

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))

# rerank all users
def init_ranking_table():
    database.client.table_operate('oj_ranking','new')
    users = database.client.table_operate('oj_users','all')
    if users[0] == 'FAIL': return users
    else: users = users[1]['data']
    sorted = []
    for i in users:
        this_user = database.client.item_operate('oj_users',i,'get')[1]
        print(i,this_user)
        del this_user['descriptions']['introduction']
        del this_user['descriptions']['user-img']
        solved = len(this_user['descriptions']['solved-problems'])
        # new = {}
        # new['name'] = users[i]
        # new['description'] = users[i]['descriptions']
        # new['solved'] = len(users[i]['descriptions']['solved-problems'])
        if len(sorted) == 0:
            sorted.append({
                'name': i,
                'description': this_user['descriptions']['description'],
                'solved': solved
            })
        else:
            for index in range(0,len(sorted)+1):
                if index == len(sorted) or sorted[index]['solved'] < solved:
                    sorted.insert(index,{
                        'name': i,
                        'description': this_user['descriptions']['description'],
                        'solved': solved
                    })
                    break

    users = {}
    index = 0
    for i in sorted:
        result = database.client.item_operate('oj_users', i['name'], 'get')
        result = result[1]
        result['ranking'] = index
        database.client.item_operate('oj_users', i['name'], 'change', result)
        database.client.item_operate('oj_ranking', index, 'new', i)
        index += 1
    
    del sorted
    return ('OK',None)

def resort_table(username:str):
    origin = database.client.table_operate('oj_ranking','all')
    user = database.client.item_operate('oj_users',username,'get')
    origin = origin[1]
    user = user[1]
    solved = user['descriptions']['solved-problems']
    origin[user['ranking']]['solved'] = solved
    # solved过的题目不会减少
    if origin[user['ranking']]['solved'] > origin[user['ranking']-1]['solved']:
        index = user['ranking'] - 1
        while origin[index+1]['solved'] > origin[index]['solved']:
            origin[index], origin[index+1] = origin[index+1], origin[index]
            index = index - 1
            if index == 0: break
        user['ranking'] = index
    elif origin[user['ranking']]['solved'] == origin[user['ranking']-1]['solved']: pass
    else:
        raise Exception("ranking--")
    database.client.item_operate('oj_users',username,'change',user)
    database.client.table_operate('oj_ranking','set',origin)

def get_ranking_count():
    return database.client.table_operate('oj_ranking','info')[1]['total_data_cnt']

def get_rankings(begin:int = 0,end:int = 10):
    result = []
    if end > get_ranking_count(): end = get_ranking_count()
    for i in range(begin,end):
        data = database.client.item_operate('oj_ranking',i,'get')[1]
        result.append([data,i])
    # result.reverse()
    return result

def get_rankings_per_page(prefix:int):
    return get_rankings(prefix,prefix + 10)

init()