import flask
from flask import Blueprint
from flask import render_template

from lib.stree.stress_env import *

app_stress_jenkins = Blueprint('stress_jenkins', __name__)

# 压测环境启动
@app_stress_jenkins.route('/stress/jenkins')
def jenkinsHtml(filename=None):
    return render_template('stress/stressConfig.html', filename=filename, htmlName="stressConfig.html")

@app_stress_jenkins.route('/stress/getImages', methods=['get'])
def opsGetImages():
    choose_env = flask.request.values.get('choose_env')
    if choose_env == "":res = {"msg": "需选择镜像获取环境", "code": 200, "data": None}
    else:
        try:
            images = streeEnvConfig().run_getImages(choose_env)
            res = {"msg": "已获得images", "code": 200, "data": {"server":images[0], "image":images[1]}}
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "获取images失败", "code": 200, "data": e}
            pass

    return json.dumps(res,ensure_ascii=False)


@app_stress_jenkins.route('/stress/configJenkins', methods=['get'])
def jenkinsConfig():
    choose_action = flask.request.values.get('choose_action')
    pod_num = flask.request.values.get('pod_num')
    serverList = flask.request.values.get('serverList').split(",")
    imageList = flask.request.values.get('imageList').split(",")
    print(serverList)
    if choose_action == "undefined":res = {"msg": "需选择命令", "code": 200, "data": None}
    elif serverList[0] == "":res = {"msg": "请选择需部署的服务", "code": 200, "data": None}
    else:
        dict_images = dict(zip(serverList, imageList))
        jenkinsMsg = streeEnvConfig().runJenkins(choose_action,dict_images,pod_num)
        res = {"msg":"Jenkins已发起","code":200,"data": {"jenkins":jenkinsMsg[0],"successProject":jenkinsMsg[1],"failProject":jenkinsMsg[2]}}
    return json.dumps(res,ensure_ascii=False)