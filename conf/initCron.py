import os,sys

# 单文件执行时配置
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("icode_test_platform")+len("icode_test_platform")]
sys.path.append(rootPath)
from bin.runMySQL import mysqlMain

path = "/var/spool/cron/crontabs/root"

sqlconnet = mysqlMain('MySQL-Database')
sql_cron = "SELECT `scene`,`times`,`scenario_id` FROM `qa_platform`.`api_auto_report_cron` WHERE `status` = 1;"
report_info = sqlconnet.fetchall(sql_cron)
del sqlconnet

with open(path, 'w',encoding='utf-8') as cron:
    cron.seek(0)
    cron.truncate()
    for line in report_info:
        hour = line['times'][0:2]
        minute = line['times'][3:5]
        cron_text = "{0} {1} * * * python /icode_test_platform/lib/py/icode_api_auto_report.py".format(minute, hour)
        cron.write(cron_text)