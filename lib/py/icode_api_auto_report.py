import os,sys,time
import json

# 单文件执行时配置
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("icode_test_platform")+len("icode_test_platform")]
sys.path.append(rootPath)
from conf.readconfig import getConfig
from bin.runMySQL import mysqlMain
from bin.runDIngTalkRobot import dingTalkMain

class icodeApiAutoReport(object):
        # 查询报告id
    def selectReport(self,report_name,scenario_id,waiting_time:int):
        sqlconnet = mysqlMain('MySQL-MeterSphere')
        report_id = []
        i = 0
        while (len(report_id) == 0 and i < waiting_time*6):  # 如果找不到报告，共等待 waiting_time 分钟
            sql_report_id = "SELECT `id` FROM `metersphere`.`api_scenario_report` WHERE `name` like %s and scenario_id = %s;"
            value = (report_name,scenario_id)
            report_id = sqlconnet.fetchall(sql_report_id,value)
            i = i + 1
            if len(report_id) == 0:time.sleep(10)  # 如果找不到报告，等待10s
        del sqlconnet
        if len(report_id) != 0:
            return report_id[0]['id']
        else:
            return False


    # 查询报告内容并整理格式
    def sqlApiAutoReport(self,report_id):
        """
        :param report_id: 报告id
        """
        # 解绑学员微信关联
        sqlconnet = mysqlMain('MySQL-MeterSphere')
        sql_report_info = "SELECT `name`,`status`,`scenario_name`,`create_time`,`end_time` FROM `metersphere`.`api_scenario_report` WHERE `id` = '%s';"%report_id
        report_info = sqlconnet.fetchall(sql_report_info)
        name = report_info[0]['name']
        status = report_info[0]['status']

        sql_content = "SELECT `content` FROM `metersphere`.`api_scenario_report_detail` WHERE `report_id` = '%s';"%report_id
        content = sqlconnet.fetchall(sql_content)
        del sqlconnet

        report_result = json.loads(str(content[0]['content'], encoding = "utf-8"))
        responseTime = report_result['scenarios'][0]['responseTime']
        total = report_result['total']
        success = report_result['success']
        error = report_result['error']
        errorContext = "\n失败详情：\n"


        if status == "Error":
            status = "<font color=red>"+status+"</font>"
            error = "<font color=red>"+str(error)+"</font>"
            # token = report_result['scenarios'][0]['requestResults'][0]['responseResult']['vars'] # 学生端定制
            # error_list = report_result['scenarios'][0]['requestResults'][2]['url']
            # error_list_body = report_result['scenarios'][0]['requestResults'][2]['responseResult']['body']
            error_num = 0
            for error_request in report_result['scenarios'][0]['requestResults']:
                if error_request['error'] == 1:
                    error_list = error_request['url']
                    error_list_body = error_request['responseResult']['body']
                    if error_list == "": error_list = "【脚本】"+error_request['name'].replace("^@~@^"," ")
                    errorContext = errorContext + "\n---\n>请求地址：" + error_list + "\n\n>响应内容：" + error_list_body + "\n"
                    error_num = error_num + 1
                if error_num == 2:
                    errorContext = errorContext + "---\n>其他失败详情请[点击链接]("+getConfig("MeterSphere-url","url")+"/#/api/automation/report/view/" + report_id + ")\n"
                    break
            errorContext = errorContext
        else:
            status = "<font color=#00cc00>"+status+"</font>"
            error = "<font color=#000000>"+str(error)+"</font>"
            errorContext = ""

        text = "接口自动化定时任务通知：\n" + \
               "\n### " + name + "\n" + \
               "\n执行环境：测试环境\n" + \
               "\n接口自动化测试结果："+ status + "\n" + \
               "\n执行请求总数：**" + str(total) + "**\n" + \
               "\n请求成功总数：**" + str(success) + "**\n" + \
               "\n请求失败总数：**" + str(error) + "**\n" + \
               "\n执行耗时：" + str(responseTime/1000) + "s\n" + \
               "\n报告详情：[链接]("+getConfig("MeterSphere-url","url")+"/#/api/automation/report/view/" + report_id + ")\n"\
               "\n"+ errorContext

        print(text)
        return text

    def main(self,choose,scene,times:str(5),scenario_id,waiting_time:int):
        """
        :param choose: 传入 debug 不会推到大群，其他不输入任何参数会推到大群
        :return:
        """
        if choose != 'debug':choose = 'test'
        report_name = scene+"-"+time.strftime("%Y-%m-%d", time.localtime())+" "+times[:-1]+"%"
        print(report_name)
        # report_id:
        # f1f5a903-02ab-a829-85c9-f3544f6c7260 1个失败
        # 119db513-32d6-edeb-e302-d0ee393f426b 成功
        # 832acafe-08d7-a5d7-08f9-f0a5194f3364 8个失败
        report_id = self.selectReport(report_name,scenario_id,waiting_time)
        if report_id:
            dingTalkMain().sendDingTalk(choose, self.sqlApiAutoReport(report_id))
        else:
            print(str(waiting_time)+"分钟内未找到报告")

if __name__=='__main__':

    # scene = "学生端上课（全链路）"
    # scenario_id = "e0b73b67-c7c6-411d-b25c-cbb1fcca0d23"
    choose = 'debug'
    waiting_time = 5 # 分钟
    sqlconnet = mysqlMain('MySQL-Database')
    times = (time.strftime("%H:%M", time.localtime()))
    print(times)
    # times = ("07:30")
    sql_cron = "SELECT `scene`,`times`,`scenario_id` FROM `qa_platform`.`api_auto_report_cron` WHERE `status` = 1 AND `times` = '%s';"%times
    report_info = sqlconnet.fetchall(sql_cron)
    del sqlconnet
    if len(report_info)!=0:
        for line in report_info:
            scene = line['scene']
            print(scene)
            times = line['times']
            scenario_id = line['scenario_id']
            icodeApiAutoReport().main(choose,scene,times,scenario_id,waiting_time) # debug, test
    else:
        print("未找到 "+times+" 计划")