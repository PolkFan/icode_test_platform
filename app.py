#-*_coding:utf8-*-
# @Author  : xuwei.fan
# @Time    : 2021-09-20

import flask
from flask import Flask, render_template, send_from_directory
from flask_caching import Cache

from ops.stress.jenkins import app_stress_jenkins
from ops.order.orderV2 import app_order_V2
from ops.tools.csvAverage import app_tools_csv
from conf.readconfig import *

app = Flask(__name__,template_folder='templates')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

UPLOAD_FOLDER = rootPath() + "/docs/import_files"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹

app.register_blueprint(app_stress_jenkins,url_prefix='/stress_jenkins')
app.register_blueprint(app_order_V2,url_prefix='/order_V2')
app.register_blueprint(app_tools_csv,url_prefix='/tools_csv')

# app_tools_csv.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹

@app.route('/favicon.ico')
def favicon(): 
    return send_from_directory(rootPath() + "/static", "favicon.ico")

@app.route('/')
def halloHtml():
    return render_template('hello.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.DEBUG = True
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True, processes=2)
