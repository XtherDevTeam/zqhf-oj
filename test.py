import os,sys,json

with open('config/users.json','r+') as file: 
    print(json.loads(file.read()))