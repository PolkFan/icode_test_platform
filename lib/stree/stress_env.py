# -*- coding: utf-8 -*-
import requests
import json
import jenkins
import os,time
import filecmp
import difflib

from conf.readconfig import *

class streeEnvConfig():
    def getDateTime(self):
        return str(time.time()*1000)

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
            pass

    def getImages(self,Authorization,times,choose):
        url = "https://mid-gw.vipthink.net"
        if choose == 'dev':dic = "ced86e844a60ee1026510aa5b790e85c"
        elif choose == 'pro':dic = '5edbb1267064ea747fba948d178041e8'
        else:dic = "bf1d7e1bc5c84856dad3e5d3d690ec7a"
        url_path = "/vipthink-devops-ops-service/api/v1/envs/"+dic+"/cluster/services/page?userId="+getConfig("crm-login","pro_id")+"&page=1&size=20&_="+times
        headers = {
            'authorization': Authorization
        }
        response = requests.request("GET", url+url_path, headers=headers)
        re=json.loads(response.text)
        list_name = [elem['name'] for elem in re['payload']['rows']]
        list_image = [elem['image'] for elem in re['payload']['rows']]
        print(list_name)
        # dict_image = dict(zip(list_name,list_image))
        return list_name,list_image

    def runJenkins(self,action,images,num):
        url = getConfig("jenkins-login","url")
        server = jenkins.Jenkins(url=url,username=getConfig("jenkins-login","username"),password=getConfig("jenkins-login","token"))

        # project = 'wdbc_project_backend/vipthink-icode-staff-api'
        # payload = {
        #     "ENV": "stress",
        #     "ACTION": action,
        #     "IMAGE": images['vipthink-icode-staff-api'],
        #     "REPLICAS": num
        # }
        # server.build_job(project, payload)

        success = []
        error = []
        for name,image in images.items():
            if action!='deploy_image':image = ''
            project = 'wdbc_project_backend/'+name
            payload = {
                "ENV": "stress",
                "ACTION": action,
                "IMAGE": image,
                "REPLICAS": num
            }
            print(project)
            try:
                server.build_job(project,payload)
                success.append(name)
            except KeyError as e:
                error.append(name)
                pass
        return "已开始构建",success,error

    def getNacosToken(self, env):
        url = getConfig("nacos-login",env) # env: test, stress
        url_path = "/nacos/v1/auth/users/login"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = "username=nacos&password=yftp6udZOOMi0oU9Y8e6"
        response = requests.request("POST", url+url_path, headers=headers, payload=payload)
        re=json.loads(response.text)
        return re['accessToken']

    def exportNacos(self,accessToken,times):
        url = getConfig("nacos-login","test")
        url_path = "/nacos/v1/cs/configs?export=true&tenant=uat&group=&appName=&dataId=&ids=&accessToken="+accessToken+"&username=nacos"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'accessToken': accessToken
        }
        response = requests.request("GET", url+url_path, headers=headers)
        with open("nacos-test-" + times + ".zip", "wb") as code:
            code.write(response.content)
        return

    def importNacos(self,accessToken,times):
        url = getConfig("nacos-login","stress")
        url_path = "/nacos/v1/cs/configs?import=true&namespace=stress&accessToken="+accessToken+"&username=nacos"
        payload = {}
        files = [
            ('file', ("nacos-test-" + times + ".zip", open("nacos-test-" + times + ".zip", 'rb'),'application/zip'))
        ]
        headers = {
            'accessToken': accessToken
        }
        response = requests.request("POST", url+url_path, headers=headers, data=payload, files=files) # , verify=False
        # print(response.text)
        # os.remove("nacos-test-" + times + ".zip")
        # re=json.loads(response.text)
        return

    def walkFile(self,path,Filelist):
        newDir = path
        if os. path.isfile(path):
            Filelist.append(path)
        ##若只是要返回文件文,使用这个
        # Filelist.append (os.path.basename(path)
        elif os.path.isdir(path):
            for s in os.listdir(path):
                # 如果需要忽略某些文件夹,使用以下代码
                # if s == "xxx":
                #     continue
                newDir = os.path.join(path, s)
                self.walkFile(newDir, Filelist)
        return Filelist

    def diffNaocs(self):
        path1 = "/Users/office/Desktop/uat"
        path2 = "/Users/office/Desktop/stress"
        file1 = self.walkFile(path1,[])
        file2 = self.walkFile(path2,[])

        # result = filecmp.cmp(file1[0], file2[0])
        list1 = [val[25:] for val in file1]
        list2 = [val[28:] for val in file2]
        tmp = [val for val in list1 if val in list2]
        for name in tmp:
            if filecmp.cmp(path1+name,path2+name) is False:
                with open(path1+name,'r')as file1,open(path2+name,'r')as file2:
                    f1 = file1.read().splitlines(keepends=True)
                    f2 = file2.read().splitlines(keepends=True)
                diff = difflib.HtmlDiff()
                result = diff.make_file(f1,f2)
                with open("/Users/office/Desktop/diff"+name+".html",'w')as f:
                    f.write(result)
                # print(path1+name)

    def delNaocs(self,accessToken,ids):
        url = getConfig("nacos-login","stress")
        url_path = "/nacos/v1/cs/configs?delType=ids&ids="+ids+"&accessToken="+accessToken+"&username=nacos"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': {"accessToken":accessToken,"tokenTtl":18000,"globalAdmin":True,"username":"nacos"}
        }
        payload = "namespaceId=stress"
        response = requests.request("DELETE", url+url_path, headers=headers, payload=payload)

    def run_getImages(self,choose):
        times = self.getDateTime()
        token = self.getCrmToken("pro")
        return self.getImages(token[0],times,choose)

    # nacos配置同步未完成
    # def run(self,action,pod_num,images):
    #     times = self.getDateTime()
    #     token = self.getCrmToken("pro")
    #     return self.getImages(token[0],times,choose)
    #     return self.runJenkins(action,images,pod_num)
    #     uat_accessToken = self.getNacosToken("uat")
    #     stree_accessToken = self.getNacosToken("stress")
    #     self.exportNacos(uat_accessToken,times)
    #     self.importNacos(stree_accessToken,times)
    #     print('end')


if __name__ == '__main__':
    env = "test"
    action = "deploy_image" # deploy_image, modify_replicas, restart
    pod_num = 1
    images = streeEnvConfig().run_getImages(env)
    # streeEnvConfig().run_jenkins(action,pod_num,server,images)