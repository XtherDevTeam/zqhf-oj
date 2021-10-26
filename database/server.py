import pickle,socket,database.authlib,database.dbapis,threading,multiprocessing,traceback,hashlib
from timeit import repeat

server = socket.socket
clientStatus = {}
threadpool = {}

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

def recv(client:socket.socket):
    ranIntoInput = False
    result = bytes()
    while True:
        try:
            now = client.recv(1024)
            if len(now) == 0:
                break
            result += now
            ranIntoInput = True
        except BlockingIOError as e:
            if ranIntoInput: break
    return result

def recv_nbytes(client:socket.socket,n:int):
    #global client
    ranIntoInput = False
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
            if ranIntoInput: break
    if len(result) != n: return None
    return result

def secure_recv(client:socket.socket):
    global server
    md5 = recv_nbytes(client,32)
    if md5 == None: raise Exception(("FAIL","Invalid data format"))
    md5.decode('utf-8')
    data = recv(client)
    while hashlib.md5(data).hexdigest() != md5:
        server.send(make_resend_packet())
        md5 = recv_nbytes(32)
        if md5 == None: raise Exception(("FAIL","Invalid data format"))
        md5.decode('utf-8')
        data = recv()
        
    return data
    

def recv_all(clientSocket:socket.socket):
    result = bytes()
    ranIntoInput = False
    while True:
        try:
            clientSocket.setblocking(0)
            current = clientSocket.recv(1024)
            clientSocket.setblocking(1)
            if len(current) == 0:
                break
            else: result += current
            ranIntoInput = True
        except BlockingIOError as e:
            if ranIntoInput: break
    return result



def processing(clientSocket:socket.socket,clientAddr:tuple,config:dict):
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
                    print('send message')
            elif clientStatus.get(clientAddr) == 'CHECK':
                recv_data = secure_recv(clientSocket)
                print(recv_data)
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
                recv_data = pickle.loads(secure_recv(clientSocket))
                print('recv from ' + str(clientAddr) + ': ', recv_data)
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
                            secure_send(clientSocket, pickle.dumps( database.dbapis.createTable(recv_data['table']) ) )
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
        except Exception as e:
            traceback.print_exc()
            secure_send(clientSocket,pickle.dumps({'status':'FAIL','data': str(e)}))
            # clientSocket.close()
            if database.dbapis.db == None: database.dbapis.openDBFile()
            database.dbapis.saveDBFile()
            break

def run(addr:str,port:str, config:dict):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((addr,port))
    server.listen(128)
    server.setblocking(0)
    while True:
        try:
            clientSocket, clientAddr = server.accept()
            clientSocket.setblocking(0)
            print('get connection:' + str(clientAddr))
            # processing(clientSocket,clientAddr,config)
            threadpool[clientAddr] = threading.Thread(target=processing,args=(clientSocket,clientAddr,config))
            threadpool[clientAddr].start()
            #threadpool[clientAddr].join()
        except BlockingIOError as e:
            print('I\'m free!','\b\b\b\b\b\b\b\b\b\b\b',end='\b')
            pass
    server.close()