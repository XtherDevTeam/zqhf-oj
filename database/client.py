import pickle
import socket

client = socket.socket

def __del__():
    close_connection()

def recv_all():
    global client
    ranIntoInput = False
    result = bytes()
    while True:
        try:
            client.setblocking(0)
            now = client.recv(1024)
            client.setblocking(1)
            if len(now) == 0:
                break
            result += now
            ranIntoInput = True
        except BlockingIOError as e:
            if ranIntoInput: break
    return result

def open_connection(server:str,port:int,username:str,password:str):
    global client
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((server,port))
    # recv all blocked
    client.setblocking(0)
    recv_data = recv_all()
    try:
        recv_data = pickle.loads(recv_data)
    except Exception as e:
        return str(recv_data)
    print(recv_data['status'])
    if recv_data['status'] == 'accept':
        return True
    elif recv_data['status'] == 'auth':
        print('need auth')
        client.send(pickle.dumps([username,password]))
        recv_data = pickle.loads(recv_all())
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
    client.send(pickle.dumps({
        'action': operation,
        'object': 'item',
        'table': tab,
        'item': name,
        'data': data
    }))
    recv_data = pickle.loads(recv_all())
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data['data'])

def table_operate(tab:str,operation:str,data:dict = {}):
    global client
    if client == None:
        return ('FAIL','Client is hot connected to server')
    client.send(pickle.dumps({
        'action': operation,
        'object': 'table',
        'table': tab,
        'data': data
    }))
    recv_data = pickle.loads(recv_all())
    if recv_data['status'] == 'OK': return ('OK',recv_data['data'])
    else: return ('FAIL',recv_data)

def close_connection():
    global client
    if client == None:
        return
    client.send(pickle.dumps({'action':'disconnect'}))
    client.close()
    return
