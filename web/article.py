import os,sys,json,web.users,config.global_config,database.client,web.ranking,markdown,time
from pickletools import int4

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))

def new_article(title:str,author:str,content:str):
    return database.client.item_operate('oj_article',title,'new',{
        'title': title,
        'author': author,
        'time': time.strftime('%Y-%m-%d %H:%M:%S Localtime',time.localtime(time.time())),
        'content': content,
        'comment': []
    })

def new_comment(id:int,author:str,content:str):
    article = get_article(id)
    article['comment'].append({
        'author': author,
        'time': time.strftime('%Y-%m-%d %H:%M:%S Localtime',time.localtime(time.time())),
        'content': content
    })

def remove_article(id:int):
    return database.client.item_operate('oj_article',id_to_name(id),'delete')

def get_article(id:int):
    result = database.client.item_operate('article',id_to_name(id),'get')
    if result[0] == 'FAIL': return None
    return result[1]['data']

def get_articles_count():
    query = database.client.table_operate('oj_article','info')
    if query[0] == 'FAIL': return 0
    return query[1]['total_data_cnt']

def get_article_names():
    query = database.client.table_operate('oj_article','all')
    if query[0] == 'FAIL': return []
    return query[1]['data']

def id_to_name(id:int):
    if type(id).__name__ == 'str': id = int(id)
    result = get_article_names()
    if id >= len(result): return None
    return result[id]

def name_to_id(name:str):
    result = get_article_names()
    try:
        return result.index(name)
    except Exception:
        return None

def get_articles(prefix:int,count:int):
    result = []
    for i in range(prefix,prefix + 10):
        this = get_article(i)
        if this == None: continue
        this['html'] = markdown.markdown(this['content'],extensions=[
            'markdown_katex'
        ],extension_configs={
            'markdown_katex': {
                'no_inline_svg': True,
                'insert_fonts_css': True,
            },
        })
        this['id'] = i
        result.append(this)
    return result