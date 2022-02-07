from io import BytesIO
from os import SEEK_SET
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

    io1 = BytesIO(pickle.dumps(data))
    io1.seek(0, SEEK_SET)

    recv_data = None

    while True:
        try:
            recv_data = pickle.loads(requests.get(
                "http://" + config.global_config.global_config['database-server-host'] + ":" + str(config.global_config.global_config['database-server-port']) + \
                "/%s/%s/%s/%s" % (session, operation, tab, name),
                files={'data': io1}
            ).content)
            break
        except Exception:
            time.sleep(0.01)
        
    
    io1.close()
    
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data['data'])

def table_operate(tab:str,operation:str,data:dict = {}):
    global session
    print("Session", session)
    if session == None:
        return ('FAIL','Client is hot connected to server')
    
    io1 = BytesIO(pickle.dumps(data))
    io1.seek(0, SEEK_SET)
    
    while True:
        try:
            recv_data = pickle.loads(requests.get(
                "http://" + config.global_config.global_config['database-server-host'] + ":" + str(config.global_config.global_config['database-server-port']) + \
                "/%s/%s/%s" % (session, operation, tab),
                files={'data': io1}
            ).content)
            break
        except Exception:
            time.sleep(0.01)
    
    io1.close()
    
    # return session
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data)

def close_connection(client:str):
    pickle.loads(requests.get(
        "http://" + config.global_config.global_config['database-server-host'] + ":" + str(config.global_config.global_config['database-server-port']) + \
        "/" + client + "/logout"
    ).content)
    print("Connection closed", session)
    return session
