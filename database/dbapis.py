import json,pickle

db = None

def saveDBFile():
    global db
    with open('database/main.db','wb+') as file:
        if db == None:
            db = {}
        file.write(pickle.dumps(db))

def exportDBFile(filename:str):
    global db
    with open(filename,'wb+') as file:
        if db == None:
            db = {}
        file.write(pickle.dumps(db))

def openDBFile():
    global db
    with open('database/main.db','rb+') as file:
        db = pickle.loads(file.read())

def createTable(name:str,type:str = 'dict'):
    # print('creating table: ' + name)
    global db
    if db == None:
        openDBFile()
    db[name] = {}
    if type == 'dict': db[name]["data"] = {}
    else: db[name]["data"] = []
    # print('success')
    return {'status':'OK', 'data': None}

def removeTable(name:str):
    global db
    if db == None: openDBFile()
    if db.get(name) == None: return {'status':'FAIL', 'data': 'mo match table found'}
    del db[name]
    return {'status':'OK', 'data': None}

def getTableInfo(name:str):
    global db
    if db == None: openDBFile()
    if db.get(name) == None: return {'status':'FAIL','data':'no match table found.'}
    # print('?',db.get(name))
    return {'status':'OK','data':{
        'name': name,
        'total_data_cnt': len(db.get(name)['data']),
    }}

def getTableData(name:str):
    global db
    if db == None: openDBFile()
    if db.get(name) == None: return {'status':'FAIL','data':'no match table found.'}
    if isinstance(db[name]['data'],dict):
        return {'status':'OK','data':{
            'name': name,
            'data': list(db.get(name)['data'].keys()),
        }}
    else: return {'status':'OK','data':{
            'name': name,
            'data': [x for x in range(0,len(db.get(name)['data']))],
        }}

def setTableData(name:str,data:dict):
    global db
    if db == None: openDBFile()
    if db.get(name) == None: return {'status':'FAIL','data':'no match table found.'}
    db[name]['data'] = data
    return {'status':'OK','data':None}


def queryItem(tab:str,name:str):
    global db
    if db == None: openDBFile()
    if db.get(tab) == None: return {'status':'FAIL','data':'no match table found.'}
    if isinstance(db.get(tab)['data'],dict):
        if db.get(tab)['data'].get(name) == None: return {'status':'FAIL','data':'no match item found.'}
    else:
        if not isinstance(name,int) or name >= len(db.get(tab)['data']): return {'status':'FAIL','data':'no match item found.'}
    return {'status':'OK', 'data': db.get(tab)['data'][name]}

def changeItem(tab:str,name:str,data):
    global db
    if db == None: openDBFile()
    if db.get(tab) == None: return {'status':'FAIL','data':'no match table found.'}
    if isinstance(db.get(tab)['data'],dict):
        if db.get(tab)['data'].get(name) == None: return {'status':'FAIL','data':'no match item found.'}
    else:
        if not isinstance(name,int) or name >= len(db.get(tab)['data']): return {'status':'FAIL','data':'no match item found.'}
    db[tab]['data'][name] = data
    return {'status':'OK', 'data': None}

def createItem(tab:str,name:str,data):
    global db
    if db == None: openDBFile()
    if db.get(tab) == None: return {'status':'FAIL','data':'no match table found.'}
    if isinstance(db.get(tab)['data'],dict):
        db[tab]['data'][name] = data
    else:
        db[tab]['data'].append(data)
    return {'status':'OK', 'data': None}

def removeItem(tab:str,name:str):
    global db
    if db == None: openDBFile()
    if db.get(tab) == None: return {'status':'FAIL','data':'no match table found.'}
    if isinstance(db.get(tab)['data'],dict):
        if db.get(tab)['data'].get(name) == None: return {'status':'FAIL','data':'no match item found.'}
    else:
        if not isinstance(name,int) or name >= len(db.get(tab)['data']): return {'status':'FAIL','data':'no match item found.'}
    del db[tab]['data'][name]
    return {'status':'OK', 'data': None}

def renameItem(tab:str,name:str,newname:str):
    global db
    if isinstance(db[tab]['data'],dict):
        item = queryItem(tab,name)
        if item['status'] != 'OK': return item
        item = item['data']
        createItem(tab,newname,item)
        return {'status':'OK', 'data': None}
    return {'status':'FAIL', 'data': 'list-like table is not support this command'}

def renameTable(tab:str,newname:str):
    global db
    if db == None: openDBFile()
    item = db.get(tab)
    if item == None: return {'status':'FAIL','data':'no match table found.'}
    createTable(newname)
    db[newname] = item