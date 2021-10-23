import pickle
import socket
import hashlib
import time

client = socket.socket

def __del__():
    close_connection()

def recv():
    global client
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
            if(time.time() - begin_recv > 2):
                print('recv timed out.')
                break
            if ranIntoInput: break
    return result

def clean_buffer(client:socket.socket):
    while True:
        try:
            client.recv(1)
        except BlockingIOError as e:
            if e.errno == 11: break

def recv_nbytes(n:int):
    global client
    ranIntoInput = False
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
            if ranIntoInput: break
    if len(result) != n: return None
    return result

def secure_recv(sendMessageWhileMd5Mismatch:bytes):
    global client
    md5 = recv_nbytes(32)
    if md5 == None: raise Exception(("FAIL","Invalid data format"))
    try:
        md5 = md5.decode('utf-8')
    except Exception: pass
    print('data:',md5)
    data = recv()
    if(sendMessageWhileMd5Mismatch==bytes()): return data
    while hashlib.md5(data).hexdigest() != md5:
        print("md5 mismatch:",hashlib.md5(data).hexdigest(),md5 )
        clean_buffer(client)
        secure_send(sendMessageWhileMd5Mismatch)
        md5 = recv_nbytes(32)
        try:
            md5 = md5.decode('utf-8')
        except Exception: pass
        if md5 == None: raise Exception(("FAIL","Invalid data format"))
        data = recv()
    return data
    

def secure_send(data:bytes):
    clean_buffer(client) # 清理缓冲区未接受的数据
    client.send(hashlib.md5(data).hexdigest().encode('utf-8'))
    client.send(data)


def open_connection(server:str,port:int,username:str,password:str):
    global client
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((server,port))
    # recv all blocked
    client.setblocking(0)
    recv_data = secure_recv(bytes())
    try:
        recv_data = pickle.loads(recv_data)
    except Exception as e:
        return str(recv_data)
    print(recv_data['status'])
    if recv_data['status'] == 'accept':
        return True
    elif recv_data['status'] == 'auth':
        print('need auth')
        secure_send(pickle.dumps([username,password]))
        recv_data = pickle.loads(secure_recv(pickle.dumps([username,password])))
        if recv_data['status'] == 'accept':
            return True
        elif recv_data['status'] == 'deny':
            return False
        else: False
    else: return False

def item_operate(tab:str,name:str,operation:str,data:dict = {}):
    global client
    if client == None:
        return ('FAIL','Client is hot connected to server')
    secure_send(pickle.dumps({
        'action': operation,
        'object': 'item',
        'table': tab,
        'item': name,
        'data': data
    }))
    recv_data = pickle.loads(secure_recv((pickle.dumps({
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
    secure_send(pickle.dumps({
        'action': operation,
        'object': 'table',
        'table': tab,
        'data': data
    }))
    recv_data = pickle.loads(secure_recv(pickle.dumps({
        'action': operation,
        'object': 'table',
        'table': tab,
        'data': data
    })))
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data)

def close_connection():
    global client
    if client == None:
        return
    secure_send(pickle.dumps({'action':'disconnect'}))
    client.close()
    return
