import database.client,config.global_config,time,markdown,urllib.parse

def init():
    print(__name__,'opened connection: ',database.client.open_connection(
        config.global_config.global_config['database-server-host'],
        config.global_config.global_config['database-server-port'],
        config.global_config.global_config['database-server-username'],
        config.global_config.global_config['database-server-password']
    ))

"""
{
    'title': '标题',
    'time': '时间',
    'content': '内容'
}
"""

def get_user_notes(username:str):
    if database.client.item_operate('oj_notebook',username,'get')[0] == 'FAIL':
        database.client.item_operate('oj_notebook',username,'new',[])
    return database.client.item_operate('oj_notebook',username,'get')[1]

def edit_user_note(username:str,id:int,note:dict):
    notes = get_user_notes(username)
    notes[id] = note
    notes[id]['time'] = time.strftime('%Y-%m-%d %H:%M:%S Localtime',time.localtime(time.time()))
    database.client.item_operate('oj_notebook',username,'change',notes)

def get_note_html(note:dict):
    note['html'] = markdown.markdown(urllib.parse.unquote(note['content']),extensions=[
        'markdown_katex'
    ],extension_configs={
        'markdown_katex': {
            'no_inline_svg': False,
            'insert_fonts_css': True,
        },
    })
    return note

def new_note(username:str, title:str, content:str):
    notes = get_user_notes(username)
    notes.append({
        'title': title,
        'time': time.strftime('%Y-%m-%d %H:%M:%S Localtime',time.localtime(time.time())),
        'content': content
    })
    database.client.item_operate('oj_notebook',username,'change',notes)

def remove_note(username:str, id:int):
    notes = get_user_notes(username)
    if id >= len(notes):
        return False
    del notes[id]
    database.client.item_operate('oj_notebook',username,'change',notes)

init()