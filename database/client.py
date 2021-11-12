import pickle
import socket
import hashlib
import time
import threading

client = socket.socket

msg_queue = []
msg_result = dict()
queue_thread = threading.Thread()

def __del__():
    close_connection()

def recv():
    global client
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

def recv_nbytes(n:int):
    global client
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

def secure_recv(sendMessageWhileMd5Mismatch:bytes):
    global client
    data = bytes()
    md5 = recv_nbytes(32)
    if md5 == None: md5 = bytes()
    try:
        md5 = md5.decode('utf-8')
        data = recv()
    except Exception: pass
    # print('data:',md5)
    if(sendMessageWhileMd5Mismatch==bytes()): return data
    while hashlib.md5(data).hexdigest() != md5:
        print("md5 mismatch:",hashlib.md5(data).hexdigest(),md5 )
        clean_buffer(client)
        secure_send(sendMessageWhileMd5Mismatch)
        md5 = recv_nbytes(32)
        try:
            md5 = md5.decode('utf-8')
            data = recv()
        except Exception: pass
        if md5 == None: md5 = bytes()
        now_time = time.time()
        time.sleep(now_time - int(now_time))
    return data
    

def secure_send(data:bytes):
    clean_buffer(client) # 清理缓冲区未接受的数据
    client.send(hashlib.md5(data).hexdigest().encode('utf-8'))
    client.send(data)


def open_connection(server:str,port:int,username:str,password:str):
    global client
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((server,port))
    # client.setblocking(0)
    # recv all blocked
    recv_data = secure_recv(bytes())
    try:
        recv_data = pickle.loads(recv_data)
    except Exception as e:
        return str(recv_data)
    # print(recv_data['status'])
    if recv_data['status'] == 'accept':
        queue_init()
        return True
    elif recv_data['status'] == 'auth':
        secure_send(pickle.dumps([username,password]))
        recv_data = pickle.loads(secure_recv(pickle.dumps([username,password])))
        if recv_data['status'] == 'accept':
            queue_init()
            return True
        elif recv_data['status'] == 'deny':
            return False
        else: False
    else: return False
    

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
        secure_send(msg[1])
        result = secure_recv(msg[1])
        msg_result[msg[0]] = result

def queue_communicate(data:bytes):
    key = hashlib.md5(str(time.time()).encode('utf-8'))
    msg_queue.append((key,data))
    while msg_result.get(key) == None:
        continue
    data = msg_result.get(key)
    del msg_result[key]
    return data

def queue_init():
    queue_thread = threading.Thread(target=queue_processor)
    queue_thread.start()
    
    print('Started queue processor')

def close_connection():
    global client
    if client == None:
        return
    secure_send(pickle.dumps({'action':'disconnect'}))
    client.close()
    return
