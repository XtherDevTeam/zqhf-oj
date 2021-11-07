import pickle,socket,database.authlib,database.dbapis,threading,traceback,hashlib,time

server = socket.socket
clientStatus = {}
threadpool = {}

class DataRecvError(Exception):
    def __init__(self,str):
        super().__init__(self,str)

def make_repeat(_str:str,c:int = 32):
    s = ''
    for i in range(0,c):
        s+=_str
    return s

def make_resend_packet():
    hash = make_repeat('f',32) + '1145141919810'
    return hash.encode('utf-8')
    
def secure_send(client:socket.socket,data:bytes):
    client.send(hashlib.md5(data).hexdigest().encode('utf-8'))
    client.send(data)

def recv_all(client:socket.socket):
    client.setblocking(0)
    ranIntoInput = False
    begin_time = time.time()
    result = bytes()
    while True:
        try:
            now = client.recv(1024)
            if len(now) == 0:
                break
            result += now
            ranIntoInput = True
        except BlockingIOError as e:
            if int(time.time()) - int(begin_time) > 1: break
            if ranIntoInput: break
            # time.sleep(0.01)
    return result

def clean_buffer(client:socket.socket):
    client.setblocking(0)
    while True:
        try:
            if client.recv(1) == b'': return
        except Exception:
            return

def recv_nbytes(client:socket.socket,n:int):
    #global client
    client.setblocking(0)
    ranIntoInput = False
    begin_time = time.time()
    result = bytes()
    while True:
        try:
            if n < 1024:
                now = client.recv(n)
                return now
            else:
                now = client.recv(1024)
            now -= 1024
            if len(now) == n:
                break
            result += now
            ranIntoInput = True
        except BlockingIOError as e:
            if int(time.time()) - int(begin_time) > 1: break
            if ranIntoInput: break
            # time.sleep(0.01)
    if len(result) != n: return None
    client.setblocking(1)
    return result

def secure_recv(client:socket.socket):
    global server
    data = bytes()
    md5 = recv_nbytes(client,32)
    if md5 == None: 
        raise DataRecvError("no data fetched")
    try:
        md5 = md5.decode('utf-8')
        data = recv_all(client)
    except Exception:
        pass
    
    while hashlib.md5(data).hexdigest() != md5:
        clean_buffer(client)
        client.send(make_resend_packet())
        md5 = recv_nbytes(client,32)
        if md5 == None: continue
        try:
            md5 = md5.decode('utf-8')
            data = recv_all(client)
        except Exception:
            # time.sleep(0.1)
            pass

    return data


def processing(clientSocket:socket.socket,clientAddr:tuple,config:dict):
    # clientSocket.setblocking(0)
    while True:
        try:
            if clientStatus.get(clientAddr) == None:
                if config.get('checker') == None or config.get('checker') == 'accept':
                    print(clientSocket,secure_send(clientSocket, pickle.dumps( {'status':'accept','data':''} ) ))
                    clientStatus[clientAddr] = 'OK'
                    print('send accept message')
                else:
                    clientStatus[clientAddr] = 'CHECK'
                    secure_send(clientSocket,pickle.dumps( {'status':'auth','data':config.get('checker')} ) )
                    print('send check message')
            elif clientStatus.get(clientAddr) == 'CHECK':
                recv_data = secure_recv(clientSocket)
                # print(recv_data)
                recv_data = pickle.loads(recv_data)
                print('checking account:', recv_data, database.authlib.checkUserInfomation(recv_data[0],recv_data[1]))
                result = database.authlib.checkUserInfomation(recv_data[0],recv_data[1])
                if result == False:
                    secure_send(clientSocket,pickle.dumps( {'status':'deny','data':''} ) )
                    clientSocket.close()
                    break
                else: secure_send(clientSocket,pickle.dumps( {'status':'accept','data':''} ) )
                clientStatus[clientAddr] = 'OK'
            elif clientStatus.get(clientAddr) == 'OK':
                # print('start process query command: ',begin_time)
                begin_time = int(time.time())
                recv_data = pickle.loads(secure_recv(clientSocket))
                query_time = int(time.time())
                # print('recv from ' + str(clientAddr) + ': ', recv_data)
                if recv_data['action'] == 'disconnect':
                    if database.dbapis.db == None: database.dbapis.openDBFile()
                    database.dbapis.saveDBFile()
                    clientSocket.close()
                    break
                if recv_data['object'] == 'item':
                    if recv_data['action'] == 'new':
                        secure_send(clientSocket,pickle.dumps( database.dbapis.createItem(recv_data['table'],recv_data['item'],recv_data['data']) ) )
                    elif recv_data['action'] == 'delete':
                        secure_send(clientSocket,pickle.dumps( database.dbapis.removeItem(recv_data['table'],recv_data['item']) ) )
                    elif recv_data['action'] == 'change':
                        secure_send(clientSocket,pickle.dumps( database.dbapis.changeItem(recv_data['table'],recv_data['item'],recv_data['data']) ) )
                    elif recv_data['action'] == 'get':
                        secure_send(clientSocket,pickle.dumps( database.dbapis.queryItem(recv_data['table'],recv_data['item']) ) )
                    else:
                        secure_send(clientSocket,pickle.dumps( {'status':'FAIL','data':'unknown command'} ) )
                elif recv_data['object'] == 'table':
                        if recv_data['action'] == 'new':
                            secure_send(clientSocket, pickle.dumps( database.dbapis.createTable(recv_data['table'],recv_data['data']) ) )
                        elif recv_data['action'] == 'delete':
                            secure_send(clientSocket,pickle.dumps( database.dbapis.removeTable(recv_data['table']) ) )
                        elif recv_data['action'] == 'info':
                            secure_send(clientSocket,pickle.dumps( database.dbapis.getTableInfo(recv_data['table']) ) )
                        elif recv_data['action'] == 'all':
                            secure_send(clientSocket,pickle.dumps( database.dbapis.getTableData(recv_data['table']) ) )
                        elif recv_data['action'] == 'set':
                            secure_send(clientSocket,pickle.dumps( database.dbapis.setTableData(recv_data['table'],recv_data['data']) ) )
                        elif recv_data['action'] == 'clear':
                            secure_send(clientSocket,pickle.dumps( database.dbapis.createTable(recv_data['table']) ) )
                        else:
                            secure_send(clientSocket,pickle.dumps( {'status':'FAIL','data':'unknown command'} ) )
                else:
                    secure_send(clientSocket,pickle.dumps( {'status':'FAIL','data':'unknown object'} ) )
                end_time = int(time.time())
                print('end query in ', end_time - begin_time, end_time - query_time, query_time - begin_time)
        except DataRecvError as e:
            # print(threading.currentThread().name, ' sleep\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b',end='')
            time.sleep(0.1)
        except Exception as e:
            traceback.print_exc()
            # secure_send(clientSocket,pickle.dumps({'status':'FAIL','data': str(e)}))
            # clientSocket.close()
            if database.dbapis.db == None: database.dbapis.openDBFile()
            database.dbapis.saveDBFile()
            print('exited')
            return

def run(addr:str,port:str, config:dict):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((addr,port))
    server.listen(128)
    # server.setblocking(0)
    while True:
        try:
            clientSocket, clientAddr = server.accept()
            print('get connection:' + str(clientAddr))
            # processing(clientSocket,clientAddr,config)
            threadpool[clientAddr] = threading.Thread(target=processing,args=(clientSocket,clientAddr,config))
            threadpool[clientAddr].start()
            #threadpool[clientAddr].join()
        except BlockingIOError as e:
            time.sleep(0.1)
            # print("I'm free\r\r\r\r\r\r\r\r",end='')
            pass
    server.close()