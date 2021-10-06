import multiprocessing as mp

tasks = []

def push_task(use_plugin:str,source:str,binary:str):
    tasks.append( [ use_plugin, source, binary ] )

def task_processor():
    while True:
        while len(tasks) == 0:
            continue
        tasks.pop()