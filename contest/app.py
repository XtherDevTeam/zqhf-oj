import json
import os
import sys
import flask
import web.config
import web.users
import demjson
import urllib.parse
import contest.judge.task
import contest.judge.judge_apis
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

def createRootTemplate(_action: str, renderText):
    logined = (flask.session.get('username') != None)
    return render_template(
        'contest_root_template.html',
        config_file=web.config.configf,
        action=_action,
        render_text=flask.Markup(renderText),
        is_logined=logined,
        user={'name': flask.session.get('username'), 'item': web.users.get_user_item(
            flask.session.get('username'))}
    )
    
@app.route('/',methods = ["GET"])
def index_of_contest_main():
    logined = (flask.session.get('username') != None)
    return createRootTemplate(
        '比赛', 
        render_template(
            'contest.html',
            logined = logined
        )
    )

def run():
    web.config.open_config_file()
    contest.judge.task.init()
    # judge.records.web.users.init()
    # judge.records.init()
    # judge.judge_apis.init()
    # web.users.init()
    app.secret_key = 'zqhf_ojserver'
    app.run(
        web.config.get_config_value("contest-server-host"),
        web.config.get_config_value("contest-server-port"),
        debug=False,
    )