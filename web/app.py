import os,sys,flask,web.config,web.users
from flask.templating import render_template

app = flask.Flask(__name__)

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

@app.route('/api',methods = ["GET"])
def index_of_api():
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
    return createRootTemplate(
        flask.session.get('username') + 'の账户管理',
        flask.render_template(
            'self.html',
            config_file = web.config.configf,
            user = { 'name':flask.session.get('username'), 'item':web.users.get_user_item(flask.session.get('username'))  }
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
    return createRootTemplate(
        username + 'の个人空间',
        flask.render_template(
            'space.html',
            config_file = web.config.configf,
            user = { 'name':username, 'item':web.users.get_user_item(username)  }
        )
    )

def run():
    web.users.open_users_file()
    web.config.open_config_file()
    flask.Flask(__name__,
                template_folder=os.getcwd()+"/web/templates/",
                static_folder=os.getcwd()+"/web/static/",
                static_url_path='/src',
                root_path = os.getcwd() + '/web/www/'
            )
    app.secret_key = 'zqhf_'+str(os.urandom(114514))
    app.run(web.config.get_config_value("server-host"),
            web.config.get_config_value("server-port"),
            debug=False,
        )