import pickle,socket,database.authlib,database.dbapis,threading,multiprocessing,traceback

server = socket.socket
clientStatus = {}
threadpool = {}

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
                    print(clientSocket,clientSocket.send( pickle.dumps( {'status':'accept','data':''} ) ))
                    clientStatus[clientAddr] = 'OK'
                    print('send accept message')
                else:
                    clientStatus[clientAddr] = 'CHECK'
                    clientSocket.send( pickle.dumps( {'status':'auth','data':config.get('checker')} ) )
                    print('send message')
            elif clientStatus.get(clientAddr) == 'CHECK':
                recv_data = recv_all(clientSocket)
                print(recv_data)
                recv_data = pickle.loads(recv_data)
                print('checking account:', recv_data, database.authlib.checkUserInfomation(recv_data[0],recv_data[1]))
                result = database.authlib.checkUserInfomation(recv_data[0],recv_data[1])
                if result == False:
                    clientSocket.send( pickle.dumps( {'status':'deny','data':''} ) )
                    clientSocket.close()
                    break
                else: clientSocket.send( pickle.dumps( {'status':'accept','data':''} ) )
                clientStatus[clientAddr] = 'OK'
            elif clientStatus.get(clientAddr) == 'OK':
                recv_data = pickle.loads(recv_all(clientSocket))
                print('recv from ' + str(clientAddr) + ': ', recv_data)
                if recv_data['action'] == 'disconnect':
                    if database.dbapis.db == None: database.dbapis.openDBFile()
                    database.dbapis.saveDBFile()
                    clientSocket.close()
                    break
                if recv_data['object'] == 'item':
                    if recv_data['action'] == 'new':
                        clientSocket.send( pickle.dumps( database.dbapis.createItem(recv_data['table'],recv_data['item'],recv_data['data']) ) )
                    elif recv_data['action'] == 'delete':
                        clientSocket.send( pickle.dumps( database.dbapis.removeItem(recv_data['table'],recv_data['item']) ) )
                    elif recv_data['action'] == 'change':
                        clientSocket.send( pickle.dumps( database.dbapis.changeItem(recv_data['table'],recv_data['item'],recv_data['data']) ) )
                    elif recv_data['action'] == 'get':
                        clientSocket.send( pickle.dumps( database.dbapis.queryItem(recv_data['table'],recv_data['item']) ) )
                    else:
                        clientSocket.send( pickle.dumps( {'status':'FAIL','data':'unknown command'} ) )
                elif recv_data['object'] == 'table':
                        if recv_data['action'] == 'new':
                            clientSocket.send( pickle.dumps( database.dbapis.createTable(recv_data['table']) ) )
                        elif recv_data['action'] == 'delete':
                            clientSocket.send( pickle.dumps( database.dbapis.removeTable(recv_data['table']) ) )
                        elif recv_data['action'] == 'info':
                            clientSocket.send( pickle.dumps( database.dbapis.getTableInfo(recv_data['table']) ) )
                        elif recv_data['action'] == 'all':
                            clientSocket.send( pickle.dumps( database.dbapis.getTableData(recv_data['table']) ) )
                        elif recv_data['action'] == 'set':
                            clientSocket.send( pickle.dumps( database.dbapis.setTableData(recv_data['table'],recv_data['data']) ) )
                        elif recv_data['action'] == 'clear':
                            clientSocket.send( pickle.dumps( database.dbapis.createTable(recv_data['table']) ) )
                        else:
                            clientSocket.send( pickle.dumps( {'status':'FAIL','data':'unknown command'} ) )
                else:
                    clientSocket.send( pickle.dumps( {'status':'FAIL','data':'unknown object'} ) )
        except Exception as e:
            traceback.print_exc()
            clientSocket.send(pickle.dumps({'status':'FAIL','data': str(e)}))
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