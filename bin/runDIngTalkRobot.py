#!/usr/bin/env python
#-*_coding:utf8-*-

import time,urllib,json,requests
import hmac,hashlib,base64
from conf.readconfig import getConfig

class dingTalkMain(object):
    # 钉钉机器人推送
    def sendDingTalk(self,choose,data):
        secret = getConfig("DingTalk",choose+"_secret")
        url = getConfig("DingTalk",choose+"_url")
        timestamp = str(round(time.time() * 1000))
        app_secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        # sign = base64.b64encode(hmac_code).decode('utf-8')
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        webhook_url = url + '&timestamp={}&sign={}'.format(timestamp, sign)
        header = {
            'Content-Type': 'application/json;charset=UTF-8',
            'charset': 'UTF-8',
        }
        markdown_report = {
            "msgtype": "markdown",
            "markdown": {
                "title": "接口自动化定时任务通知",
                "text": data
            },
            "at": {
                "atMobiles": 15602384112,
                "isAtAll": False
            }
        }
        send_data = json.dumps(markdown_report).encode('UTF-8')
        print(webhook_url)
        response = requests.request("POST", webhook_url, headers=header, data=send_data)
        print(response.text)
        print("已发送")