import json
import os,sys,flask,web.config,web.users,demjson,urllib.parse,judge.problems,judge.task,judge.records,judge.plugins,atexit
from flask.templating import render_template

app = flask.Flask(__name__,static_url_path='/src')

def createRootTemplate( _action:str,renderText ):
    logined = (flask.session.get('username') != None)
    return render_template( 
        'root_template.html',
        config_file = web.config.configf,
        action = _action,
        render_text = flask.Markup(renderText),
        is_logined = logined,
        user = { 'name':flask.session.get('username'), 'item':web.users.get_user_item(flask.session.get('username'))  }
    )

@app.route('/',methods = ["GET"])
def index():
    logined = (flask.session.get('username') != None)
    if not logined:
        return flask.redirect('/login?reason=You are not signed in!')
    return createRootTemplate(
        '主页',
        flask.render_template(
            'index.html',
            config_file = web.config.configf
        )
    )

@app.route('/api',methods = ["GET","POST"])
def index_of_api():
    if flask.request.method == "GET":
        request_item = flask.request.args.get('request')
        if request_item == None:
            return {'status':'error', 'reason': 'no request argument found.'}
        elif request_item == 'login':
            if flask.request.args.get('usr') == None or flask.request.args.get('pwd') == None:
                return {'status':'error', 'reason': 'username or password is empty.'}
            if web.users.get_user_item(flask.request.args.get('usr')) == None:
                return {'status':'error', 'reason': 'user not found.'}
            if web.users.check_user(flask.request.args.get('usr'),flask.request.args.get('pwd')) == False:
                return {'status':'error', 'reason': 'username or password doesn\'t match'}
            flask.session['username'] = flask.request.args.get('usr')
            return {'status':'success'}
        elif request_item == 'signup':
            if flask.request.args.get('usr') == None or flask.request.args.get('pwd') == None or flask.request.args.get('invitecode') == None:
                return {'status':'error', 'reason': 'username or password is empty.'}
            if web.users.get_user_item(flask.request.args.get('usr')) != None:
                return {'status':'error', 'reason': 'username already exist.'}
            if web.config.get_config_value('invite-code') != flask.request.args.get('invitecode'):
                return {'status':'error', 'reason': 'wrong invite code.'}
            web.users.new_user( flask.request.args.get('usr'),1,flask.request.args.get('pwd') )
            return {'status':'success'}
        elif request_item == 'logout':
            if flask.session.get('username') == None:
                return {'status':'error', 'reason':'no matches cookies found.'}
            else:
                del flask.session['username']
            return {'status':'success'}
        elif request_item == 'remove_problem':
            if flask.session.get('pid') == None or int(flask.session.get('pid')) >= judge.problems.get_problems_count():
                return {'status':'error', 'reason':'invalid or empty problem id.'}
            judge.problems.remove_problem(int(flask.session.get('pid')))
            return {'status':'success'}
    elif flask.request.method == "POST":
        request_item = flask.request.args.get('request')
        if request_item == None:
            return {'status':'error', 'reason': 'no request argument found.'}
        if flask.session.get('username') == None:
            return {'status':'error', 'reason':'no matches cookies found.'}
        if(request_item == 'updateUserSpace'):
            fill = web.users.get_user_item(flask.session['username'])['descriptions']
            fill['description'] = flask.request.form.get('description')
            fill['introduction'] = flask.request.form.get('introduction')
            web.users.set_user_descriptions(flask.session.get('username'),fill)
            print(web.users.get_user_item(flask.session.get('username')))
            return {'status':'success'}
        elif(request_item == 'postProblem'):
            problem = flask.request.form.get('problem_json')
            if problem == None:
                return {'status':'error', 'reason': 'invalid problem format'}
            problem = json.loads(problem)
            problem['info']['author'] = flask.session.get('username')
            pid = judge.problems.new_problem(problem["info"])
            judge.problems.createJudgeFile(pid,problem["input"],problem["output"])
            return {'status':'success'}
        elif(request_item == 'editProblem'):
            problem = flask.request.form.get('problem_json')
            if problem == None:
                return {'status':'error', 'reason': 'invalid problem format'}
            problem = json.loads(problem)
            problem['info']['author'] = flask.session.get('username')
            pid = int(flask.request.form.get('action'))
            judge.problems.edit_problem(pid,problem['info'])
            judge.problems.createJudgeFile(pid,problem["input"],problem["output"])
            return {'status':'success'}
        elif(request_item == 'submitAnswer'):
            content = flask.request.form.get('json')
            if content == None:
                return {'status':'error', 'reason': 'invalid json format'}
            content = json.loads(content)
            print('submit get',content)
            io_file = judge.problems.get_judge_file(int(content['pid'])) # 0-> in, 1-> out
            if io_file == None:
                return {'status':'error', 'reason': 'problem not exist'}
            with open('tmp/temp.' + content['ext'],'w+') as file:
                file.write(content['code'])
            task_id = judge.task.push_task(
                content['lang'],urllib.parse.unquote(io_file[0]),
                urllib.parse.unquote(io_file[1]),
                'temp.' + content['ext'],
                'temp.bin',
                flask.session.get('username'),
                content['pid']
            )
            return {'status':'success', 'task_id': task_id}

@app.route('/login',methods = ["GET"])
def index_of_login():
    return createRootTemplate(
        '登入',
        flask.render_template(
            'login.html',
            config_file = web.config.configf,
            reason = flask.request.args.get('reason')
        )
    )

@app.route('/signup',methods = ["GET"])
def index_of_signup():
    return createRootTemplate(
        '注册',
        flask.render_template(
            'signup.html',
            config_file = web.config.configf,
            reason = flask.request.args.get('reason')
        )
    )

@app.route('/user/self',methods = ["GET"])
def index_of_user_self():
    logined = (flask.session.get('username') != None)
    if not logined:
        return flask.redirect('/login?reason=You are not signed in!')
    finalUser = { 'name':flask.session.get('username'), 'item':web.users.get_user_item(flask.session.get('username'))  }
    return createRootTemplate(
        flask.session.get('username') + '的账户管理',
        flask.render_template(
            'self.html',
            config_file = web.config.configf,
            user = finalUser
        )
    )

@app.route('/user/<username>',methods = ["GET"])
def index_of_user_profile(username:str):
    if(web.users.get_user_item(username) == None):
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file = web.config.configf,
                reason = '用户' + username + '不存在'
            )
        )
    print(web.users.get_user_item(username))
    return createRootTemplate(
        username + '的个人空间',
        flask.render_template(
            'space.html',
            config_file = web.config.configf,
            user = { 'name':username, 'item':web.users.get_user_item(username)  },
            ACedCount = len(web.users.get_user_item(username)['descriptions']['solved-problems']),
            introduction = urllib.parse.unquote(web.users.get_user_item(username)['descriptions']['introduction'])
        )
    )

@app.route('/problems', methods = ["GET"])
def index_of_problems():
    prefix = 0
    if flask.request.args.get('index') != None:
        prefix = int(flask.request.args.get('index')) * 10
    print('fuckyou!',judge.problems.get_problems_per_page(prefix,10))
    return createRootTemplate(
        '题库',
        flask.render_template(
            'problems.html',
            config_file = web.config.configf,
            problems = judge.problems.get_problems_per_page(prefix,10),
            problems_count = judge.problems.get_problems_count(),
            now_index = int(prefix / 10),
            total_index = int(judge.problems.get_problems_count() / 10),
            now_prefix = prefix,
            user = { 'name':flask.session.get('username'), 'item':web.users.get_user_item(flask.session.get('username'))  }
        )
    )

@app.route('/problems/post', methods = ["GET"])
def index_of_post_problem():
    logined = (flask.session.get('username') != None)
    if not logined:
        return flask.redirect('/login?reason=You are not signed in!')
    return createRootTemplate(
        '创建题目',
        flask.render_template(
            'post-problem.html',
            config_file = web.config.configf,
            origin = None
        )
    )

@app.route('/problems/edit', methods = ["GET"])
def index_of_edit_problem():
    logined = (flask.session.get('username') != None)
    if not logined:
        return flask.redirect('/login?reason=You are not signed in!')
    pid = flask.request.args.get('pid')
    if pid == None or int(pid) > judge.problems.get_problems_count():
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file = web.config.configf,
                reason = str(pid) + '不是一个有效的题目编号'
            )
        )
    pid = int(pid)
    return createRootTemplate(
        '修改题目',
        flask.render_template(
            'post-problem.html',
            config_file = web.config.configf,
            problem_id = pid,
            origin = judge.problems.get_problem(pid),
            tags = json.dumps(judge.problems.get_problem(pid)["tags"]),
            judge_file = judge.problems.get_judge_file(pid),
            input_examples = json.dumps(judge.problems.get_problem(pid)["input_example"]),
            output_examples = json.dumps(judge.problems.get_problem(pid)["output_example"])
        )
    )

@app.route('/problems/<pid>', methods = ["GET"])
def index_of_problem(pid:str):
    pid = int(pid)
    if pid > judge.problems.get_problems_count():
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file = web.config.configf,
                reason = str(pid) + '不是一个有效的题目编号'
            )
        )
    return createRootTemplate(
        judge.problems.get_problem(pid)["name"],
        flask.render_template(
            'problem.html',
            logined = (flask.session.get('username') != None),
            problem_id = pid,
            problem = judge.problems.get_problem(pid),
            example_count = len(judge.problems.get_problem(pid)["input_example"])
        )
    )

@app.route('/problems/<pid>/post', methods = ["GET"])
def index_of_post_answer(pid):
    logined = (flask.session.get('username') != None)
    if not logined:
        return flask.redirect('/login?reason=You are not signed in!')
    pid = int(pid)
    if pid > judge.problems.get_problems_count():
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file = web.config.configf,
                reason = str(pid) + '不是一个有效的题目编号'
            )
        )
    # judge.plugins.load_plugins_list()
    return createRootTemplate(
        '提交答案' + judge.problems.get_problem(pid)["name"],
        flask.render_template(
            'post-answer.html',
            problem_id = pid,
            problem = judge.problems.get_problem(pid),
            support_lang = judge.plugins.plugins_list,
            support_lang_json = json.dumps(judge.plugins.plugins_list)
        )
    )

@app.route('/judge_status/<id>', methods = ["GET"])
def index_of_judge_status(id):
    id = int(id)
    if id >= judge.records.get_record_count():
        return createRootTemplate(
            '错误',
            flask.render_template(
                'error.html',
                config_file = web.config.configf,
                reason = str(id) + '不是一个有效的评测结果编号'
            )
        )
    task_result = judge.records.get_record(id)
    return createRootTemplate(
        '测试结果' + str(id),
        flask.render_template(
            'judge-result.html',
            config_file = web.config.configf,
            jid = id,
            status = task_result[0],
            output = task_result[1].replace('\n','<br>'),
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
        problem_id = int(i[0][3])
        problem_name = judge.problems.get_problem(problem_id)['name']
        records_per_page.append({
            'record': i[0],
            'problem_id': problem_id,
            'problem_name': problem_name,
            'real_record_id': i[1]['record_id']
        })

    return createRootTemplate(
        '提交记录',
        flask.render_template(
            'records.html',
            config_file = web.config.configf,
            now_index = int(prefix / 10),
            total_index = int(len(records) / 10),
            records = records_per_page
        )
    )

def run():
    web.config.open_config_file()
    judge.task.init()
    #judge.records.web.users.init()
    #judge.records.init()
    #judge.problems.init()
    # web.users.init()
    app.secret_key = 'zqhf_'+str(os.urandom(114514))
    app.run(web.config.get_config_value("server-host"),
            web.config.get_config_value("server-port"),
            debug=False,
        )

@atexit.register
def when_program_exit():
    print(__name__,'exited')
    web.users.database.client.close_connection()