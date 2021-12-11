import json
import os
import sys
from types import prepare_class
import flask
import web.config
import web.users
import demjson
import urllib.parse
import judge.problems
import judge.task
import judge.records
import judge.plugins
import atexit
import base64
import time
import web.ranking
import web.problemList
import markdown
import web.notebook
import time
import web.image
import io
from flask.templating import render_template

app = flask.Flask(__name__, static_url_path='/src')


def get_bulletin_realid(index: int):
    query_result = web.users.database.client.table_operate('oj_board', 'all')
    return query_result[1]['data'][index]


def get_bulletin_fakeid(index: str):
    query_result = web.users.database.client.table_operate('oj_board', 'all')
    return query_result[1]['data'].index(index)


def get_bulletin(index: int):
    query_result = web.users.database.client.table_operate('oj_board', 'all')
    query_result = web.users.database.client.item_operate(
        'oj_board', query_result[1]['data'][index], 'get')
    if query_result[0] != 'OK':
        return None
    try:
        # print(query_result)
        query_result[1]['content-html'] = markdown.markdown(urllib.parse.unquote(query_result[1]['content']), extensions=[
            'markdown_katex',
            'markdown.extensions.extra',
            'markdown.extensions.codehilite'
        ], extension_configs={
            'markdown_katex': {
                'no_inline_svg': False,
                'insert_fonts_css': True,
            },
        })
        query_result[1]['content-html'] = urllib.parse.quote(
            query_result[1]['content-html'])
    except Exception as e:
        # print(e)
        query_result[1]['content-html'] = ''
    return query_result[1]


def new_bulletin(title: str, content: str, time: str):
    query_result = web.users.database.client.item_operate('oj_board', title, 'new', {
        'title': title,
        'content': content,
        'time': time
    })
    return query_result


def edit_bulletin(id: int, title: str, content: str, time: str):
    query_result = web.users.database.client.item_operate('oj_board', get_bulletin_realid(id), 'change', {
        'title': title,
        'content': content,
        'time': time
    })
    return query_result


def remove_bulletin(index: int):
    query_result = web.users.database.client.item_operate(
        'oj_board', get_bulletin_realid(index), 'delete')
    if query_result[0] != 'OK':
        return None
    return query_result[1]


def get_bulletin_count():
    query_result = web.users.database.client.table_operate('oj_board', 'info')
    if query_result[0] != 'OK':
        return None
    return query_result[1]['total_data_cnt']


def get_bullets(begin: int, end: int):
    count = get_bulletin_count()
    if begin > end:
        begin = count
    if end > count:
        end = count
    if begin < 0:
        begin = 0
    if end < 0:
        end = 0
    result = []
    for i in range(begin, end):
        result.append([get_bulletin(i), i])
    return result


def get_board(prefix: int):
    total = get_bulletin_count()
    # print('debug',total,prefix)
    result = get_bullets(prefix, prefix + 10)
    return result


def createRootTemplate(_action: str, renderText):
    logined = (flask.session.get('username') != None)
    return render_template(
        'root_template.html',
        config_file=web.config.configf,
        action=_action,
        render_text=flask.Markup(renderText),
        is_logined=logined,
        user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
            flask.session.get('username'))}
    )


@app.route('/', methods=["GET"])
def index():
    logined = (flask.session.get('username') != None)

    board = get_board(get_bulletin_count() - 10)
    board.reverse()
    return createRootTemplate(
        '主页',
        flask.render_template(
            'index.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            board=board,
            rankingTop10=web.ranking.get_rankings_per_page(0)
        )
    )


@app.route('/lists', methods=["GET"])
def index_of_problem_lists():
    now_index = 0
    if flask.request.args.get('index') != None:
        now_index = int(flask.request.args.get('index'))
    prefix = now_index * 10
    lists = web.problemList.get_problem_lists_per_page(prefix)
    return createRootTemplate(
        '题单列表',
        flask.render_template(
            'plist-list.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            lists=lists,
            now_index=now_index,
            total_index=int(
                len(web.problemList.get_problem_list_names()) / 10),
        )
    )

@app.route('/user-image', methods=["GET"])
def index_of_user_image_main():
    logined = (flask.session.get('username') != None)
    
    userimg_cnt = web.image.get_image_cnt(flask.session.get('username'))
    
    return createRootTemplate(
        '我的图床',
        flask.render_template(
            'image-manage.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            userimg_cnt = userimg_cnt
        )
    )

@app.route('/user-image/upload', methods=["POST"])
def index_of_image_upload():
    logined = (flask.session.get('username') != None)
    
    img = flask.request.files.get('img')
    dest = io.BytesIO()
    img.save(dest)
    dest.seek(0)
    web.image.new_image(flask.session['username'],dest.read())
    del dest
    return flask.redirect('/user-image')

@app.route('/user-image/<int:imgid>/delete', methods=["GET"])
def index_of_user_image_delete(imgid:int):
    logined = (flask.session.get('username') != None)
    
    username = flask.session['username']
    if web.image.remove_image(username,imgid) == False: return {'status':'error', 'reason': 'remove_image(username,imgid) failed.'}
    return {'status':'success'}

@app.route('/user-image/<username>/<int:imgid>', methods=["GET"])
def index_of_user_image_response(username:str,imgid:int):
    img = web.image.get_image(username,imgid)
    if img == False:
        return {
            'status': 'error',
            'reason': 'get_image(username,imgid) failed.'
        }
    response = flask.Response(img,mimetype='image/jpeg')
    return response

@app.route('/lists/post', methods=["GET"])
def index_of_problem_list_post():
    logined = (flask.session.get('username') != None)

    return createRootTemplate(
        '创建题单',
        flask.render_template(
            'plist-post.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            list=None,
        )
    )


@app.route('/lists/<name>', methods=["GET"])
def index_of_problem_list(name):
    _list = web.problemList.get_problem_list(
        web.problemList.id_to_name(int(name)))
    if _list == None:
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='题单' + name + '不存在'
            )
        )
    return createRootTemplate(
        _list['name'],
        flask.render_template(
            'plist-view.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            list=_list,
            problems=judge.problems.get_selected_problems_detail(
                _list['content'])
        )
    )


@app.route('/lists/<name>/edit', methods=["GET"])
def index_of_problem_list_edit(name):
    logined = (flask.session.get('username') != None)

    _list = web.problemList.get_problem_list(
        web.problemList.id_to_name(int(name)))
    if _list == None:
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='题单' + name + '不存在'
            )
        )
    return createRootTemplate(
        '编辑题单',
        flask.render_template(
            'plist-post.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            list=_list,
        )
    )


@app.route('/bulletins', methods=["GET"])
def index_of_bulletin_list():
    logined = (flask.session.get('username') != None)
    now_index = 0
    if flask.request.args.get('index') != None:
        now_index = int(flask.request.args.get('index'))
    prefix = now_index * 10
    board = get_board(prefix)
    board.reverse()
    return createRootTemplate(
        '公告列表',
        flask.render_template(
            'bulletins_list.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            board=board,
            now_index=now_index,
            total_index=int(get_bulletin_count() / 10),
        )
    )


@app.route('/bulletins/<id>/edit', methods=["GET"])
def index_of_edit_bulletin(id):
    logined = (flask.session.get('username') != None)
    if web.users.get_user_item(flask.session.get('username')) == None or web.users.get_user_item(flask.session.get('username'))['premission'] != 0:
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='用户' + flask.session.get('username') + '权限不足'
            )
        )

    bulletin = get_bulletin(int(id))
    if bulletin == None:
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='公告不存在'
            )
        )

    return createRootTemplate(
        '修改公告',
        flask.render_template(
            'create-bulletin.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            origin=bulletin,
            bulletin_id=int(id),
        )
    )


@app.route('/tags/<tag>')
def index_of_tags_matcher(tag):
    problems = judge.problems.get_match_tags_problems(tag)
    return createRootTemplate(
        '查询标签:' + tag,
        flask.render_template(
            'tagsMatcher.html',
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            config_file=web.config.configf,
            problems=problems,
            tag=tag
        )
    )


@app.route('/bulletins/<id>', methods=["GET"])
def index_of_show_bulletin(id):
    bulletin = get_bulletin(int(id))
    if bulletin == None:
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='公告不存在'
            )
        )
    return createRootTemplate(
        bulletin['title'],
        flask.render_template(
            'bulletin.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            bulletin=bulletin,
            bulletin_id=int(id),
        )
    )
    pass


@app.route('/ranking', methods=["GET"])
def index_of_ranking():
    prefix = 0
    if flask.request.args.get('index') != None:
        prefix = int(flask.request.args.get('index')) * 10
    board = web.ranking.get_rankings_per_page(prefix)
    now_index = 0
    if flask.request.args.get('index') != None:
        now_index = int(flask.request.args.get('index'))

    return createRootTemplate(
        '排名列表',
        flask.render_template(
            'ranking.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            ranking=board,
            now_index=now_index,
            total_index=int(web.ranking.get_ranking_count() / 10),
        )
    )


@app.route('/bulletins/post', methods=["GET"])
def index_of_post_bulletin():
    logined = (flask.session.get('username') != None)
    if web.users.get_user_item(flask.session.get('username')) == None or web.users.get_user_item(flask.session.get('username'))['premission'] != 0:
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='用户' + flask.session.get('username') + '权限不足'
            )
        )

    return createRootTemplate(
        '创建公告',
        flask.render_template(
            'create-bulletin.html',
            config_file=web.config.configf,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))},
            origin=None
        )
    )


@app.route('/api', methods=["GET", "POST"])
def index_of_api():
    if flask.request.method == "GET":
        request_item = flask.request.args.get('request')
        if request_item == None:
            return {'status': 'error', 'reason': 'no request argument found.'}, '500', {'Access-Control-Allow-Origin': '*'}
        elif request_item == 'login':
            if flask.request.args.get('usr') == None or flask.request.args.get('pwd') == None:
                return {'status': 'error', 'reason': 'username or password is empty.'}, '500', {'Access-Control-Allow-Origin': '*'}
            if web.users.get_user_item(flask.request.args.get('usr')) == None:
                return {'status': 'error', 'reason': 'user not found.'}, '500', {'Access-Control-Allow-Origin': '*'}
            if web.users.check_user(flask.request.args.get('usr'), flask.request.args.get('pwd')) == False:
                return {'status': 'error', 'reason': 'username or password doesn\'t match'}, '500', {'Access-Control-Allow-Origin': '*'}
            flask.session['username'] = flask.request.args.get('usr')
            return {'status': 'success'}, '200', {'Access-Control-Allow-Origin': '*'}
        elif request_item == 'userImg':
            name = flask.request.args.get('name')
            if name == None or name == '':
                return {'status': 'error', 'reason': 'username is empty'}, '500', {'Access-Control-Allow-Origin': '*'}
            item = web.users.get_user_item(name)
            if item == None:
                return {'status': 'error', 'reason': 'user doesn\' t exist.'}, '500', {'Access-Control-Allow-Origin': '*'}
            response = flask.make_response(base64.decodebytes(
                item['descriptions']['user-img'][23:].encode('utf-8')))
            response.mimetype = 'image/jpeg'
            return response, '200', {'Access-Control-Allow-Origin': '*'}
        elif request_item == 'signup':
            if flask.request.args.get('usr') == None or flask.request.args.get('pwd') == None or flask.request.args.get('invitecode') == None:
                return {'status': 'error', 'reason': 'username or password is empty.'}, '500', {'Access-Control-Allow-Origin': '*'}
            if web.users.get_user_item(flask.request.args.get('usr')) != None:
                return {'status': 'error', 'reason': 'username already exist.'}, '500', {'Access-Control-Allow-Origin': '*'}
            if web.config.get_config_value('invite-code') != flask.request.args.get('invitecode'):
                return {'status': 'error', 'reason': 'wrong invite code.'}, '500', {'Access-Control-Allow-Origin': '*'}
            web.users.new_user(flask.request.args.get(
                'usr'), 1, flask.request.args.get('pwd'))
            return {'status': 'success'}, '200', {'Access-Control-Allow-Origin': '*'}
        elif request_item == 'logout':
            if flask.session.get('username') == None:
                return {'status': 'error', 'reason': 'no matches cookies found.'}, '500', {'Access-Control-Allow-Origin': '*'}
            else:
                del flask.session['username']
            return {'status': 'success'}, '200', {'Access-Control-Allow-Origin': '*'}
        elif request_item == 'remove_problem':
            if flask.session.get('username') != None and web.users.get_user_item(flask.session.get('username'))['premission'] == 2:
                return {'status': 'error', 'reason': 'premission denied'}, '403', {'Access-Control-Allow-Origin': '*'}
            if flask.request.args.get('pid') == None or int(flask.request.args.get('pid')) > judge.problems.get_problems_count():
                # print('count: ',judge.problems.get_problems_count())
                return {'status': 'error', 'reason': 'invalid or empty problem id.'}, '500', {'Access-Control-Allow-Origin': '*'}
            judge.problems.remove_problem(int(flask.request.args.get('pid')))
            return {'status': 'success'}, '200', {'Access-Control-Allow-Origin': '*'}
        elif request_item == 'remove_bulletin':
            if flask.session.get('username') != None and web.users.get_user_item(flask.session.get('username'))['premission'] == 2:
                return {'status': 'error', 'reason': 'premission denied'}, '500', {'Access-Control-Allow-Origin': '*'}
            if flask.request.args.get('id') == None or int(flask.request.args.get('id')) > get_bulletin_count():
                return {'status': 'error', 'reason': 'invalid or empty bulletin id.'}, '500', {'Access-Control-Allow-Origin': '*'}
            remove_bulletin(int(flask.request.args.get('id')))

            return {'status': 'success'}, '200', {'Access-Control-Allow-Origin': '*'}
        elif(request_item == 'removeNote'):
            if flask.session.get('username') != None and web.users.get_user_item(flask.session.get('username'))['premission'] == 2:
                return {'status': 'error', 'reason': 'premission denied'}, '500', {'Access-Control-Allow-Origin': '*'}
            id = flask.request.args.get('action')
            try:
                id = int(id)
            except Exception:
                return {'status': 'error', 'reason': 'invalid note number'}, '500', {'Access-Control-Allow-Origin': '*'}
            web.notebook.remove_note(flask.session['username'], id)
            return {'status': 'success'}, '200', {'Access-Control-Allow-Origin': '*'}
        elif request_item == 'remove_plist':
            if flask.session.get('username') != None and web.users.get_user_item(flask.session.get('username'))['premission'] == 2:
                return {'status': 'error', 'reason': 'premission denied'}, '500', {'Access-Control-Allow-Origin': '*'}
            if flask.request.args.get('id') == None or int(flask.request.args.get('id')) > get_bulletin_count():
                return {'status': 'error', 'reason': 'invalid or empty bulletin id.'}, '500', {'Access-Control-Allow-Origin': '*'}
            web.problemList.remove_problem_list(
                web.problemList.id_to_name(int(flask.request.args.get('id'))))
            return {'status': 'success'}, '200', {'Access-Control-Allow-Origin': '*'}

    elif flask.request.method == "POST":
        if flask.session.get('username') != None and web.users.get_user_item(flask.session.get('username'))['premission'] == 2:
            return {'status': 'error', 'reason': 'premission denied'}
        request_item = flask.request.args.get('request')
        if request_item == None:
            return {'status': 'error', 'reason': 'no request argument found.'}
        if flask.session.get('username') == None:
            return {'status': 'error', 'reason': 'no matches cookies found.'}
        if(request_item == 'changeUserImg'):
            if flask.session.get('username') == None:
                return {'status': 'error', 'reason': 'no matches cookies found.'}
            img = flask.request.files.get('user-img')
            # print(img)
            img.save('./tmp/userimg.jpeg')
            with open('./tmp/userimg.jpeg', 'rb+') as file:
                f = file.read()
                if (len(f) >= 4194304):
                    os.remove('./tmp/userimg.jpeg')
                    return {'status': 'error', 'reason': 'file too large.'}
                image_base64 = str(base64.b64encode(f), encoding='utf-8')
                userinfo = web.users.get_user_item(
                    flask.session.get('username'))
                userinfo['descriptions']['user-img'] = 'data:image/jpeg;base64,' + image_base64
                web.users.set_user_descriptions(
                    flask.session.get('username'), userinfo['descriptions'])
            os.remove('./tmp/userimg.jpeg')
            return flask.redirect('/user/self')
        
        if(request_item == 'updateUserSpace'):
            fill = web.users.get_user_item(flask.session['username'])[
                'descriptions']
            fill['description'] = flask.request.form.get('description')
            fill['introduction'] = flask.request.form.get('introduction')
            web.users.set_user_descriptions(
                flask.session.get('username'), fill)
            # print(web.users.get_user_item(flask.session.get('username')))
            return {'status': 'success'}
        
        elif(request_item == 'postProblem'):
            problem = flask.request.form.get('problem_json')
            if problem == None:
                return {'status': 'error', 'reason': 'invalid problem format'}
            problem = json.loads(problem)
            problem['info']['author'] = flask.session.get('username')
            pid = judge.problems.new_problem(problem["info"])
            judge.problems.createJudgeFile(
                pid, problem["input"], problem["output"])
            return {'status': 'success'}
        
        elif(request_item == 'editProblem'):
            problem = flask.request.form.get('problem_json')
            if problem == None:
                return {'status': 'error', 'reason': 'invalid problem format'}
            problem = json.loads(problem)
            problem['info']['author'] = flask.session.get('username')
            pid = int(flask.request.form.get('action'))
            judge.problems.edit_problem(pid, problem['info'])
            judge.problems.createJudgeFile(
                pid, problem["input"], problem["output"])
            return {'status': 'success'}
        
        elif(request_item == 'editNote'):
            note_content = json.loads(flask.request.form.get('json'))['info']
            id = flask.request.form.get('action')
            if id == 'new':
                web.notebook.new_note(
                    flask.session['username'], note_content['title'], note_content['content'])
            else:
                web.notebook.edit_user_note(
                    flask.session['username'], int(id), note_content)
            return {'status': 'success'}
        
        elif(request_item == 'submitAnswer'):
            content = flask.request.form.get('json')
            if content == None:
                return {'status': 'error', 'reason': 'invalid json format'}
            content = json.loads(content)
            # print('submit get',content)
            io_file = judge.problems.get_judge_file(
                int(content['pid']))  # 0-> in, 1-> out
            if io_file == None:
                return {'status': 'error', 'reason': 'problem not exist'}
            with open('tmp/temp.' + content['ext'], 'w+') as file:
                file.write(content['code'])
            task_id = judge.task.push_task(
                content['lang'], urllib.parse.unquote(io_file[0]),
                urllib.parse.unquote(io_file[1]),
                'temp.' + content['ext'],
                'temp.bin',
                flask.session.get('username'),
                content['pid']
            )
            return {'status': 'success', 'task_id': task_id}
        
        elif(request_item == 'postBulletin'):
            bulletin = flask.request.form.get('problem_json')
            if bulletin == None:
                return {'status': 'error', 'reason': 'invalid post format'}
            bulletin = json.loads(bulletin)
            new_bulletin(bulletin['title'], bulletin['content'], time.strftime(
                '%Y-%m-%d %H:%M:%S Localtime', time.localtime(time.time())))
            return {'status': 'success'}
        elif(request_item == 'editBulletin'):
            bulletin = flask.request.form.get('problem_json')
            if bulletin == None:
                return {'status': 'error', 'reason': 'invalid problem format'}
            bulletin = json.loads(bulletin)
            id = int(flask.request.form.get('action'))
            new_bulletin(bulletin['title'], bulletin['content'], time.strftime(
                '%Y-%m-%d %H:%M:%S Localtime', time.localtime(time.time())))
            if get_bulletin_realid(id) != bulletin['title']:
                remove_bulletin(id)
            return {'status': 'success'}
        elif(request_item == 'postList'):
            _list = flask.request.form.get('json')
            if _list == None:
                return {'status': 'error', 'reason': 'invalid post format'}
            _list1 = json.loads(_list)['info']
            # print(_list1)
            web.problemList.new_problem_list(_list1['name'], flask.session.get(
                'username'), _list1['description'], _list1['content'])
            return {'status': 'success'}

        elif(request_item == 'editList'):
            _list = flask.request.form.get('json')
            if _list == None:
                return {'status': 'error', 'reason': 'invalid post format'}
            _list1 = json.loads(_list)['info']
            web.problemList.new_problem_list(_list1['name'], flask.session.get(
                'username'), _list1['description'], _list1['content'])
            if _list1['oldname'] != _list1['name']:
                web.problemList.remove_problem_list(_list1['oldname'])

            return {'status': 'success'}


@app.route('/login', methods=["GET"])
def index_of_login():
    return createRootTemplate(
        '登入',
        flask.render_template(
            'login.html',
            config_file=web.config.configf,
            reason=flask.request.args.get('reason')
        )
    )


@app.route('/signup', methods=["GET"])
def index_of_signup():
    return createRootTemplate(
        '注册',
        flask.render_template(
            'signup.html',
            config_file=web.config.configf,
            reason=flask.request.args.get('reason')
        )
    )


@app.route('/user/self', methods=["GET"])
def index_of_user_self():
    logined = (flask.session.get('username') != None)
    finalUser = {'name': flask.session.get(
        'username'), 'item': web.users.get_user_item(flask.session.get('username'))}
    return createRootTemplate(
        flask.session.get('username') + '的账户管理',
        flask.render_template(
            'self.html',
            config_file=web.config.configf,
            user=finalUser
        )
    )


@app.route('/notebook', methods=['GET'])
def index_of_notebook():
    logined = (flask.session.get('username') != None)

    notebook = web.notebook.get_user_notes(flask.session['username'])
    return createRootTemplate(
        '我的笔记',
        flask.render_template(
            'notebook.html',
            notebook=notebook,
            notebook_json=json.dumps(notebook)
        )
    )


@app.route('/notebook/new', methods=['GET'])
def index_of_new_note():
    logined = (flask.session.get('username') != None)
    return flask.render_template(
        'note-edit.html',
        noteid='new'
    )


@app.route('/notebook/edit/<id>', methods=['GET'])
def indxe_of_edit_note(id):
    logined = (flask.session.get('username') != None)
    content = web.notebook.get_user_notes(flask.session['username'])
    if int(id) >= len(content):
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='笔记' + id + '不存在'
            )
        )

    return flask.render_template(
        'note-edit.html',
        noteid=id,
        note=content[int(id)]
    )


@app.route('/notebook/preview/<id>', methods=['GET'])
def index_of_preview_note(id):
    logined = (flask.session.get('username') != None)
    content = web.notebook.get_user_notes(flask.session['username'])
    try:
        id = int(id)
    except Exception:
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='不合法的笔记编号:' + id
            )
        )
    if id >= len(content):
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='笔记' + str(id) + '不存在'
            )
        )

    return flask.render_template(
        'note-preview.html',
        note=web.notebook.get_note_html(content[id])
    )


@app.route('/user/<username>', methods=["GET"])
def index_of_user_profile(username: str):
    if(web.users.get_user_item(username) == None):
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason='用户' + username + '不存在'
            )
        )
    # print(web.users.get_user_item(username))
    return createRootTemplate(
        username + '的个人空间',
        flask.render_template(
            'space.html',
            config_file=web.config.configf,
            user={'name': username, 'item': web.users.get_user_item(username)},
            ACedCount=len(web.users.get_user_item(username)[
                          'descriptions']['solved-problems']),
            introduction=web.users.get_user_descriptions(
                username)['introduction-html'],
        )
    )


@app.route('/problems', methods=["GET"])
def index_of_problems():
    prefix = 0
    if flask.request.args.get('index') != None:
        prefix = int(flask.request.args.get('index')) * 10
    # print('fuckyou!',judge.problems.get_problems_per_page(prefix,10))
    return createRootTemplate(
        '题库',
        flask.render_template(
            'problems.html',
            config_file=web.config.configf,
            problems=judge.problems.get_problems_per_page(prefix, 10),
            problems_count=judge.problems.get_problems_count(),
            now_index=int(prefix / 10),
            total_index=int(judge.problems.get_problems_count() / 10),
            now_prefix=prefix,
            user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
                flask.session.get('username'))}
        )
    )


@app.route('/problems/post', methods=["GET"])
def index_of_post_problem():
    logined = (flask.session.get('username') != None)
    return createRootTemplate(
        '创建题目',
        flask.render_template(
            'post-problem.html',
            config_file=web.config.configf,
            origin=None
        )
    )


@app.route('/problems/edit', methods=["GET"])
def index_of_edit_problem():
    logined = (flask.session.get('username') != None)
    pid = flask.request.args.get('pid')
    if pid == None or int(pid) > judge.problems.get_problems_count():
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason=str(pid) + '不是一个有效的题目编号'
            )
        )
    pid = int(pid)
    return createRootTemplate(
        '修改题目',
        flask.render_template(
            'post-problem.html',
            config_file=web.config.configf,
            problem_id=pid,
            origin=judge.problems.get_problem(pid),
            tags=json.dumps(judge.problems.get_problem(pid)["tags"]),
            judge_file=judge.problems.get_judge_file(pid),
            input_examples=json.dumps(
                judge.problems.get_problem(pid)["input_example"]),
            output_examples=json.dumps(
                judge.problems.get_problem(pid)["output_example"])
        )
    )


@app.route('/problems/<pid>', methods=["GET"])
def index_of_problem(pid: str):
    pid = int(pid)
    if pid > judge.problems.get_problems_count():
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason=str(pid) + '不是一个有效的题目编号'
            )
        )
    return createRootTemplate(
        judge.problems.get_problem(pid)["name"],
        flask.render_template(
            'problem.html',
            logined=(flask.session.get('username') != None),
            problem_id=pid,
            problem=judge.problems.get_problem(pid),
            example_count=len(judge.problems.get_problem(pid)["input_example"])
        )
    )


@app.route('/problems/<pid>/post', methods=["GET"])
def index_of_post_answer(pid):
    logined = (flask.session.get('username') != None)
    pid = int(pid)
    if pid > judge.problems.get_problems_count():
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason=str(pid) + '不是一个有效的题目编号'
            )
        )
    # judge.plugins.load_plugins_list()
    return createRootTemplate(
        '提交答案' + judge.problems.get_problem(pid)["name"],
        flask.render_template(
            'post-answer.html',
            problem_id=pid,
            problem=judge.problems.get_problem(pid),
            support_lang=judge.plugins.plugins_list,
            support_lang_json=json.dumps(judge.plugins.plugins_list)
        )
    )


@app.route('/judge_status/<id>', methods=["GET"])
def index_of_judge_status(id):
    id = int(id)
    if id >= judge.records.get_record_count():
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason=str(id) + '不是一个有效的评测结果编号'
            )
        )
    task_result = judge.records.get_record(id)
    return createRootTemplate(
        '测试结果' + str(id),
        flask.render_template(
            'judge-result.html',
            config_file=web.config.configf,
            jid=id,
            status=task_result[0],
            output=task_result[1].replace('\n', '<br>'),
        )
    )


@app.route('/records')
def index_of_judge_record():
    prefix = 0
    if flask.request.args.get('index') != None:
        prefix = int(flask.request.args.get('index')) * 10
    records = judge.records.get_records_per_page(prefix)
    records_per_page = []
    for i in records:
        try:
            problem_id = int(i[0][3])
            problem_name = judge.problems.get_problem(problem_id)['name']
            records_per_page.append({
                'record': i[0],
                'problem_id': problem_id,
                'problem_name': problem_name,
                'real_record_id': i[1]['record_id']
            })
        except Exception as e:
            print(e, judge.records.database.client.item_operate(
                'oj_records', i[1]['record_id'], 'delete'))

    return createRootTemplate(
        '提交记录',
        flask.render_template(
            'records.html',
            config_file=web.config.configf,
            now_index=int(prefix / 10),
            total_index=int(judge.records.get_record_count() / 10),
            records=records_per_page
        )
    )

@app.before_request
def check_banned_status():
    logined = (flask.session.get('username') != None)
    if web.config.configf["not-login-check"]:
        if not logined:
            if flask.request.path.startswith('/src'): return None
            if flask.request.path.startswith('/api'): return None
            if flask.request.path.startswith('/login'): return None
            if flask.request.path.startswith('/signup'): return None
            return flask.redirect('/login?reason=请先登录!')
    else:
        pass
    
    if flask.session.get('username') != None and web.users.get_user_item(flask.session.get('username'))['premission'] == 2:
        if flask.request.path.startswith('/src'): return None
        if flask.request.path.startswith('/api'): return None
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file=web.config.configf,
                reason=flask.session.get('username') + '已被封禁!请询问服务器管理员以了解原因.'
            )
        )
    return None

def run():
    web.config.open_config_file()
    judge.task.init()
    # judge.records.web.users.init()
    # judge.records.init()
    # judge.problems.init()
    # web.users.init()
    app.secret_key = 'zqhf_ojserver'
    app.run(web.config.get_config_value("server-host"),
            web.config.get_config_value("server-port"),
            debug=False,
            )


@atexit.register
def when_program_exit():
    print(__name__, 'exited')
    web.users.database.client.close_connection()
