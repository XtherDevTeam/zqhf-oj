from io import BytesIO
import os
import pickle,database.authlib,database.dbapis,threading,hashlib,time,config.global_config,flask

# from werkzeug.wrappers import response

server = flask.Flask(__name__)

threadpool = {}

def covertToNum(numstr:str):
    num = numstr
    if num.isnumeric():
        num = int(num)
    
    return num

class DataRecvError(Exception):
    def __init__(self,str):
        super().__init__(self,str)

session_pool = []

def check_session(session:str):
    if session_pool.count(session) == False: return False
    return True

def remove_session(session:str):
    if session_pool.count(session):
        del session_pool[session_pool.index(session)]

def response_pickle(data):
    return flask.send_file(BytesIO(pickle.dumps(data)), 'application/zqhf-oj-database-response')

@server.route('/<session>/get/<table>/<name>')
def get_data(session, table, name):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    name = covertToNum(name)
    return response_pickle(database.dbapis.queryItem(table, name))

@server.route('/<session>/change/<table>/<name>')
def set_data(session, table, name):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    name = covertToNum(name)
    data = BytesIO(bytes())
    flask.request.files.get("data").save(data)
    data.seek(0,os.SEEK_SET)
    return response_pickle(database.dbapis.changeItem(table, name, data.read()))

@server.route('/<session>/new/<table>/<name>')
def create_data(session, table, name):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    name = covertToNum(name)
    data = BytesIO(bytes())
    flask.request.files.get("data").save(data)
    data.seek(0,os.SEEK_SET)
    return response_pickle(database.dbapis.createItem(table, name, data.read()))

@server.route("/<session>/new/<table>@<type>")
def create_table(session, table, type):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    return response_pickle(database.dbapis.createTable(table, type))

@server.route("/<session>/delete/<table>")
def remove_table(session, table):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    return response_pickle(database.dbapis.removeTable(table))

@server.route("/<session>/all/<table>")
def table_data(session, table):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    return response_pickle(database.dbapis.getTableData(table))

@server.route("/<session>/info/<table>")
def table_info(session, table):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    return response_pickle(database.dbapis.getTableInfo(table))

@server.route("/<session>/clear/<table>")
def table_clear(session, table):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    return response_pickle(database.dbapis.createTable(table))

@server.route("/<session>/delete/<table>/<name>")
def remove_data(session, table, name):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    name = covertToNum(name)
    return response_pickle(database.dbapis.removeItem(table, name))

@server.route("/login/<username>:<password>")
def user_login(username, password):
    if database.authlib.checkUserInfomation(username, password):
        session = hashlib.md5((username + ":" + password + "_" + str(int(time.time()))).encode('utf-8')).hexdigest()
        session_pool.append(session)
        return response_pickle({"status": "OK", "data": session})
    else:
        return response_pickle({"status": "error", "message": "incorrect login"})
    
@server.route("/<session>/logout")
def user_logout(session):
    if not check_session(session):
        return response_pickle({"status": "error", "message": "invalid session"})
    
    remove_session(session)
    return response_pickle({"status": "OK"})
    
    
def auto_backup_proc():
    now_time = 0
    last_backup_time = 0
    last_save_time = 0
    while True:
        if now_time - last_save_time >= 300:
            print('Event: Auto save started.')
            database.dbapis.saveDBFile()
            last_save_time = time.time()
        if now_time - last_backup_time >= 3600:
            print('Event: Auto backup started.')
            time_str = time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time()))
            database.dbapis.exportDBFile(config.global_config.database_server_config['auto-backup-path']+'/db-backup-' + time_str + '.db')
            last_backup_time = time.time()
        now_time = time.time()
        time.sleep(0.01)
        pass
    
def run_server():
    database.dbapis.openDBFile()
    server.run( config.global_config.global_config['database-server-host'], config.global_config.global_config['database-server-port'] )
    threadpool['autobackup'] = threading.Thread(target=auto_backup_proc)
    threadpool['autobackup'].run()
