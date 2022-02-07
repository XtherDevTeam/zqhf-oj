import os,sys,json

configf = {}

def sync_config_file():
    with open('config/config.json','w+') as file:
        file.write( json.dumps(configf) )

def open_config_file():
    temp = None
    with open('config/config.json','r+') as file:
        temp = json.loads(file.read())
    global configf
    configf = temp

def get_config_value(key:str):
    open_config_file()
    return configf[key]

def set_config_value(key:str,item):
    configf[key] = item
    sync_config_file()