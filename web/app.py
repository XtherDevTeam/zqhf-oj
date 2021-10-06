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
        user = { 'name':flask.session.get('username') }
    )

@app.route('/',methods = ["GET"])
def index():
    return createRootTemplate(
        '主页',
        flask.render_template(
            'index.html',
            config_file = web.config.configf
        )
    )

@app.route('/login',methods = ["GET"])
def index():
    return createRootTemplate(
        '登入',
        flask.render_template(
            'login.html',
            config_file = web.config.configf
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
    app.run(web.config.get_config_value("server-host"),
            web.config.get_config_value("server-port"),
            debug=False,
        )