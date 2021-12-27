import flask
from flask import Blueprint
from flask import Flask, request, render_template
from flask import send_from_directory, jsonify, make_response

import json,time

from lib.py.csv_segmentation import *


app_tools_csv = Blueprint('tools_csv', __name__)
# app_tools_csv.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹

basedir = rootPath()  # 获取当前项目的绝对路径 # 允许上传的文件后缀
UPLOAD_FOLDER = basedir + "/docs/import_files"

# 切分CSV
@app_tools_csv.route('/csvAverage')
def csvAveragePackgeHtml(filename=None):
    return render_template('tools/csvAverage.html', filename=filename, htmlName="csvAverage.html")

@app_tools_csv.route('py/csvAverage', methods=['get'])
def csvAverageScript():
    filename = flask.request.values.get('filename')
    dividenum = flask.request.values.get('dividenum')
    if filename == '':res = {"msg":"filename不能为空","code":0}
    elif dividenum == '':res = {"msg":"dividenum不能为空","code":0}

    if csvAverage(filename, int(dividenum)):res = {"msg":"切分成功","code":0}
    else:res = {"msg":"切分失败","code":0}
    return json.dumps(res,ensure_ascii=False)


# 判断文件是否合法
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'csv','CSV'}
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# 具有上传功能的页面
@app_tools_csv.route('/upload')
def upload_testHtml():
    return render_template('tools/upload.html', htmlName="upload.html")

@app_tools_csv.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    htmlName = flask.request.values.get('htmlName')
    file_dir = os.path.join(basedir, UPLOAD_FOLDER)  # 拼接成合法文件夹地址
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = f.filename
        f.save(os.path.join(file_dir, fname))  # 保存文件到upload目录
        return render_template("tools/"+htmlName, filename=fname ,htmlName=htmlName)
    else:
        return jsonify({"code": 1001,"data":"null", "msg": "上传失败"})

# file download
@app_tools_csv.route("/download/<path:filename>", methods=['GET','POST'])
def downloader(filename):
    filepath = rootPath()+"/docs/export_files/"
    if os.path.exists(filepath+filename):
        return send_from_directory(filepath, filename, as_attachment=True)  # as_attachment=True  下载
    else:
        return "未找到文件"

# show photo
@app_tools_csv.route('/show/<string:filename>', methods=['GET'])
def show_photo(filename):
    file_dir = os.path.join(basedir, app_tools_csv.config['UPLOAD_FOLDER'])
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(file_dir, '%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass