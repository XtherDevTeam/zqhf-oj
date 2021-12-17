from io import BytesIO
import pickle
import socket
import hashlib
import time
import threading
import requests
import config.global_config

client = None
session = None

server = 0
username = 0
password = 0
port = 0

msg_queue = []
msg_result = dict()
queue_thread = threading.Thread()


def open_connection_real():
    session = pickle.loads(requests.get(
        "http://" + config.global_config.global_config['database-server-host'] + ":" + str(config.global_config.global_config['database-server-port']) + \
        "/login/" + username + ":" + password
    ).content)['data']
    return session
    
def open_connection(s:str,p:int,u:str,pwd:str):
    global server
    global port 
    global username 
    global password
    global client
    global session
    server,port,username,password = (s,p,u,pwd)
    session = open_connection_real()
    return True

def item_operate(tab:str,name:str,operation:str,data:dict = {}):
    global session
    if session == None:
        return ('FAIL','Client is hot connected to server')

    recv_data = pickle.loads(requests.get(
        "http://" + config.global_config.global_config['database-server-host'] + ":" + str(config.global_config.global_config['database-server-port']) + \
        "/%s/%s/%s/%s" % (session, operation, tab, name),
        files={'data': BytesIO(pickle.dumps(data))}
    ).content)
    
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data['data'])

def table_operate(tab:str,operation:str,data:dict = {}):
    global session
    print("Session", session)
    if session == None:
        return ('FAIL','Client is hot connected to server')
    recv_data = pickle.loads(requests.get(
        "http://" + config.global_config.global_config['database-server-host'] + ":" + str(config.global_config.global_config['database-server-port']) + \
        "/%s/%s/%s" % (session, operation, tab),
        files={'data': BytesIO(pickle.dumps(data))}
    ).content)
    # return session
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data)

def close_connection(client:str):
    session = pickle.loads(requests.get(
        "http://" + config.global_config.global_config['database-server-host'] + ":" + str(config.global_config.global_config['database-server-port']) + \
        "/" + client + "/logout"
    ).content)['data']
    print("normal session", session)
    return session
