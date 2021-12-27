# -*- coding: utf-8 -*-
import requests
import json
import pandas as pd
import os, time

import oss2
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from conf.readconfig import *

# 文件地址
import_excel_path = rootPath() + "/docs/import_files/"
order_error_code = (10000004,10000006,500003,9000004,500005)

class orderImportPackageV2():
    def orderXlsx(self,channel_id,name,area_code,phone,hourId,hour_price,filename=None):
        i=0
        title = ["*第三方订单号","*收款渠道ID","用户姓名","*手机区号","*手机号","用户类型","用户ID","*套餐ID","*订单支付金额（元）","*支付时间","*支付方式","*渠道id","获得原因","扩展信息","是否需要地址","收件人","国家","联系电话","省","市","区","详细地址","用户备注"]
        #title = ["第三方订单号","收款渠道ID","用户姓名","*手机区号","*手机号","用户类型","用户ID","*套餐SKUID","*订单支付金额（元）","*支付时间","*支付方式","*渠道id","获得原因","扩展信息","是否需要地址","收件人","国家","联系电话","省","市","区","详细地址","用户备注"]
        df = pd.DataFrame(columns=title)
        now_time = time.localtime()
        # df.loc[1] = title

        while i != len(name):
            imputInfo = [int(time.strftime("%Y%m%d%H%M%S", now_time))+i+1,0,name[i],area_code[i],phone[i],"","",hourId,hour_price,
                         time.strftime("%Y-%m-%d %H:%M:%S", now_time),"wxpay",channel_id,1999,
                         "{\"ad_id\":\"123\",\"team_id\":\"123\"}",0,"","","","","","","",""]
            df.loc[i + 1] = imputInfo
            i = i + 1

        xlsx_name = time.strftime("%Y年%m月%d日", now_time) + "-编程测试-" + time.strftime("%Y%m%d%H%M%S", now_time) + ".xlsx"
        df.to_excel(import_excel_path+xlsx_name, sheet_name='导入主表', index=False)
        size_B = os.path.getsize(import_excel_path+xlsx_name)
        # print(import_excel_path+xlsx_name)
        print("xlsx生成成功！"+str(size_B))
        return xlsx_name,size_B

    # 获取CRMtoken
    def getCrmToken(self,choose_url):
        auth_url = getConfig("auth-url",choose_url)
        url_path = "/v1/auth/admin/token"
        payload = json.dumps({
            "username": getConfig("crm-login",choose_url+"_phone"),
            "password": getConfig("crm-login",choose_url+"_pwd"),
            "__fields": "token,uid"
        })
        headers = {
            'content-type': 'application/json'
        }
        response = requests.request("POST", auth_url+url_path, headers=headers, data=payload)
        re=json.loads(response.text)
        try:
            return re['data']['token'],re['data']['uid']
        except KeyError as e:
            # 异常时，执行该块
            return False, e

    # 获取签名
    def getSign(self,choose_url,Authorization,file_name,file_size):
        attch_api_url = getConfig("attch-api-url",choose_url)
        url_path = "/v1/attach/getSign"
        payload = json.dumps({"name":file_name,
                              "dir":"uploads/images",
                              "mime":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              "ext":"xlsx",
                              "size":file_size,
                              "driver":"tencent_oss",
                              "code":"platform-trade"
        })
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", attch_api_url+url_path, headers=headers, data=payload) # , verify=False
        # print(response.text)
        re=json.loads(response.text)
        if int(re['code']) in order_error_code:return int(re['code']),re['message']
        file_id = re['data']['id']
        secret_id = json.loads(re['data']['ossToken'])['credentials']['tmpSecretId']  # 替换为用户的 SecretId
        secret_key = json.loads(re['data']['ossToken'])['credentials']['tmpSecretKey']  # 替换为用户的 SecretKey
        upRegion = re['data']['region']  # 替换为用户的 region
        # COS支持的所有region列表参见https://www.qcloud.com/document/product/436/6224
        sessionToken = json.loads(re['data']['ossToken'])['credentials']['sessionToken']
        ossDomain = re['data']['ossDomain']
        bucket = re['data']['bucket']
        path = re['data']['path']
        print("获取腾讯oss签名成功！")
        return secret_id,secret_key,upRegion,sessionToken,bucket,path,file_id,ossDomain

    # 腾讯云上传
    def oss_tencent(self,secret_id,secret_key,region,session_token,bucket,oss_path,file_name):
        scheme = 'https'  # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=session_token, Scheme=scheme)
        # config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=sessionToken, Domain=upDomain)
        # 2. 获取客户端对象
        client = CosS3Client(config)

        print(import_excel_path + file_name)
        response = client.upload_file(
            Bucket=bucket,
            LocalFilePath=import_excel_path + file_name,
            Key=oss_path,
            PartSize=1,
            MAXThread=10,
            EnableMD5=False
        )
        # print(response['ETag'])
        os.remove(import_excel_path + file_name)
        print("xlsx上传至腾讯oss成功！本地xlsx文件已删除")

    # 上传成功通知
    def importNotify(self,choose_url,Authorization,oss_file_id):
        attch_api_url = getConfig("attch-api-url",choose_url)
        url_path = "/v1/attach/notify"
        payload = json.dumps({"id":oss_file_id,"status":1})
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", attch_api_url+url_path, headers=headers, data=payload)
        # print(response.text)
        print("上传成功通知请求成功！")

    # 确认上传成功
    def urlImport(self,choose_url,Authorization,xlsx_oss_path,fileName):
        gw_url = getConfig("gw-url",choose_url)
        url_path = "/api/trade_order/v1/admin/orderImport/urlImport"
        payload = json.dumps({"fileUrl":xlsx_oss_path,
                              "fileName":fileName,
                              "operatorId":getConfig("crm-login",choose_url+"_id"),
                              "operatorName":getConfig("crm-login",choose_url+"_name")
        })
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", gw_url+url_path, headers=headers, data=payload)
        print(response.text)
        re=json.loads(response.text)
        status = True
        batchNum = re['data']['batchNum']
        importRecordId = re['data']['importRecordId']
        failReasonLists = [elem['failReason'] for elem in re['data']['importFailDtls']]
        if batchNum is None:status = False
        print("确认上传成功！")
        return batchNum,importRecordId,status,failReasonLists

    # 查询审批列表
    def dtlList(self,choose_url,Authorization,batchNum):
        gw_url = getConfig("gw-url",choose_url)
        url_path = "/api/trade_order/v1/admin/orderImport/importRecord/dtlList"
        payload = json.dumps({
            "pageNo":1,
            "pageSize":100,
            "batchNum":batchNum,
            "status":"WAIT_APPROVAL"
        })
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", gw_url+url_path, headers=headers, data=payload)
        # print(response.text)
        re = json.loads(response.text)
        lists = [elem['recordDtlId'] for elem in re['data']]
        print(lists)
        print("xlsx列表获取成功！")
        return lists

    # 导入审批通过
    def auditDtls(self,choose_url,Authorization,batchNum,lists):
        gw_url = getConfig("gw-url",choose_url)
        url_path = "/api/trade_order/v1/admin/orderImport/importRecord/auditDtls"
        payload = json.dumps({
            "recordDtlIds":lists,
            "batchNum":batchNum,
            "auditStatus":"APPROVAL_SUCCESS",
            "remarks":"脚本导入"
        })
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", gw_url+url_path, headers=headers, data=payload)
        # print(response.text)
        print("导入完成！")
        return True,"success"

    # 主流程
    def run(self,choose_url,Authorization,name,area_code,phone,hourId,hour_price,channel_id):
        if choose_url != 'test': channel_id = 467977
        if Authorization == "":Authorization = self.getCrmToken(choose_url)[0]
        if Authorization is False:return False, "登录失败"
        try:
            # 主代码块
            # xlsx_file = self.orderXlsx("张三",86,14700000065,31791779,0.01,None)
            xlsx_file = self.orderXlsx(channel_id,name, area_code, phone, hourId, hour_price)
            ossinfo = self.getSign(choose_url, Authorization, xlsx_file[0],xlsx_file[1])
            if ossinfo[0] in order_error_code:return False, ossinfo[1]
            self.oss_tencent(ossinfo[0], ossinfo[1], ossinfo[2], ossinfo[3], ossinfo[4], ossinfo[5], xlsx_file[0])
            self.importNotify(choose_url, Authorization, ossinfo[6])
            importRecord = self.urlImport(choose_url, Authorization, ossinfo[7] + ossinfo[5], xlsx_file[0])
            if importRecord[2] is False:return False,importRecord[3]
            lists = self.dtlList(choose_url, Authorization, importRecord[0])
            self.auditDtls(choose_url, Authorization, importRecord[0], lists)
            return True, "Success"
            pass
        except KeyError as e:
            # 异常时，执行该块
            return False, "False"
            pass
        except IndexError as e:
            # 异常时，执行该块
            return False, "False"
            pass
        finally:
            # 无论异常与否，最终执行该块
            pass


if __name__ == '__main__':
    choose_url = "test" # test, pro
    Authorization = ''
    nameList = ['小明']
    area_codeList = [86]
    phoneList = [14514500005]
    sku_id = 31818547
    sku_price = 101
    orderImportPackageV2().run(choose_url,Authorization,nameList,area_codeList,phoneList,sku_id,sku_price)
    # orderImportPackageV2().orderXlsx("张三","86","14700000065",31791779,0.01,None)