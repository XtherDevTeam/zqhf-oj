import pickle
import socket
import hashlib
import time
import threading

client = socket.socket

server = 0
username = 0
password = 0
port = 0

msg_queue = []
msg_result = dict()
queue_thread = threading.Thread()

def recv(client:socket.socket):
    client.setblocking(0)
    ranIntoInput = False
    result = bytes()
    begin_recv = time.time()
    while True:
        try:
            now = client.recv(1024)
            if len(now) == 0:
                break
            result += now
            ranIntoInput = True
        except BlockingIOError as e:
            if(time.time() - begin_recv > 1):
                print('recv timed out.')
                break
            if ranIntoInput: break
    client.setblocking(1)
    return result

def clean_buffer(client:socket.socket):
    client.setblocking(0)
    while True:
        try:
            if client.recv(1) == b'': return
        except Exception:
            return

def recv_nbytes(client:socket.socket,n:int):
    client.setblocking(0)
    ranIntoInput = False
    begin_recv = time.time()
    result = bytes()
    while True:
        try:
            if n < 1024:
                now = client.recv(n)
                return now
            else:
                now = client.recv(1024)
            n -= 1024
            if len(now) == n:
                break
            result += now
            ranIntoInput = True
        except BlockingIOError as e:
            if(time.time() - begin_recv > 1):
                print('recv timed out.')
                break
            if ranIntoInput: break
    if len(result) != n: return None
    client.setblocking(1)
    return result

def secure_recv(client:socket.socket,sendMessageWhileMd5Mismatch:bytes):
    data = bytes()
    retry_cnt = 0
    md5 = recv_nbytes(client,32)
    if md5 == None: md5 = bytes()
    try:
        md5 = md5.decode('utf-8')
        data = recv(client)
    except Exception: pass
    # print('data:',md5)
    if(sendMessageWhileMd5Mismatch==bytes()): return data
    while hashlib.md5(data).hexdigest() != md5:
        retry_cnt = retry_cnt + 1
        print("md5 mismatch:",hashlib.md5(data).hexdigest(),md5 )
        clean_buffer(client)
        secure_send(client,sendMessageWhileMd5Mismatch)
        md5 = recv_nbytes(client,32)
        try:
            md5 = md5.decode('utf-8')
            data = recv(client)
        except Exception: pass
        if md5 == None: md5 = bytes()
        if retry_cnt >= 5: break
        now_time = time.time()
        time.sleep(now_time - int(now_time))
    return data
    

def secure_send(client:socket.socket,data:bytes):
    clean_buffer(client) # 清理缓冲区未接受的数据
    client.send(hashlib.md5(data).hexdigest().encode('utf-8'))
    client.send(data)


def open_connection_real():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((server,port))
    # client.setblocking(0)
    # recv all blocked
    recv_data = secure_recv(client,bytes())
    try:
        recv_data = pickle.loads(recv_data)
    except Exception as e:
        return str(recv_data)
    # print(recv_data['status'])
    if recv_data['status'] == 'accept':
        # queue_init()
        return client
    elif recv_data['status'] == 'auth':
        secure_send(client,pickle.dumps([username,password]))
        recv_data = pickle.loads(secure_recv(client,pickle.dumps([username,password])))
        if recv_data['status'] == 'accept':
            # queue_init()
            return client
        elif recv_data['status'] == 'deny':
            return False
        else: False
    else: return False
    
def open_connection(s:str,p:int,u:str,pwd:str):
    global server
    global port 
    global username 
    global password 
    server,port,username,password = (s,p,u,pwd)
    queue_init()
    return True

def item_operate(tab:str,name:str,operation:str,data:dict = {}):
    global client
    if client == None:
        return ('FAIL','Client is hot connected to server')

    recv_data = pickle.loads(queue_communicate((pickle.dumps({
        'action': operation,
        'object': 'item',
        'table': tab,
        'item': name,
        'data': data
    }))))
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data['data'])

def table_operate(tab:str,operation:str,data:dict = {}):
    global client
    if client == None:
        return ('FAIL','Client is hot connected to server')
    recv_data = pickle.loads(queue_communicate(pickle.dumps({
        'action': operation,
        'object': 'table',
        'table': tab,
        'data': data
    })))
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data)

def queue_processor():
    while True:
        while len(msg_queue) == 0:
            time.sleep(0.01)
            continue
        msg = msg_queue[-1]
        msg_queue.pop()
        # msg is a tuple
        secure_send(msg[2],msg[1])
        result = secure_recv(msg[2],msg[1])
        msg_result[msg[0]] = result

def queue_communicate(data:bytes):
    client = open_connection_real()
    if client == False: return False
    if client == None: return None
    
    key = hashlib.md5(str(time.time()).encode('utf-8'))
    msg_queue.append((key,data,client))
    while msg_result.get(key) == None:
        continue
    data = msg_result.get(key)
    del msg_result[key]
    
    close_connection(client)
    return data

def queue_init():
    queue_thread = threading.Thread(target=queue_processor)
    queue_thread.start()
    
    print('Started queue processor')

def close_connection(client:socket.socket):
    if client == None:
        return
    secure_send(client,pickle.dumps({'action':'disconnect'}))
    client.close()
    return
