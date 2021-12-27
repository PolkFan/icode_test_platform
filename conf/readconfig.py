
from configparser import ConfigParser
import os,stat,platform

project_name = "icode_test_platform"
host_window = r"C:\Windows\System32\drivers\etc\\"[:-1]
host_linux = r"/etc/"


def getConfig(sysname,key):
    ini_file = "/config.ini"
    cfg = ConfigParser()
    # 读取文件内容
    cfg.read(os.path.split(os.path.realpath(__file__))[0] + ini_file, encoding="utf-8")
    return eval(cfg.get(sysname,key))

#获取项目根目录
def rootPath():
    curPath = os.path.abspath(os.path.dirname(__file__))
    rootPath = curPath[:curPath.find(project_name)+len(project_name)]
    return rootPath


def filePath():
    # curPath = os.path.abspath(os.path.dirname(__file__))
    # rootPath = curPath[curPath.find(project_name)+len(project_name):]
    curPath = os.path.split(os.path.realpath(__file__))[0]
    return curPath

def editHosts(type):
    original_hosts = "original_hosts"  # 初始hosts
    gray_hosts = "gray_hosts"  # 初始+灰度hosts
    local_hosts = "hosts"  # 当前系统hosts
    hosts_path = rootPath() + "/conf/"

    if platform.system() == "Windows":path = host_window
    else:path = host_linux

    # path = "/Users/office/Desktop/diff/"

    if os.path.exists(hosts_path+"original_hosts") is False:
        os.chmod(path+local_hosts,stat.S_IREAD|stat.S_IWUSR|stat.S_IEXEC)
        with open(path+local_hosts, 'r',encoding='utf-8') as f_hosts, open(hosts_path+original_hosts, 'w',encoding='utf-8') as f_original:
            for txt in f_hosts:
                f_original.write(txt)
        with open(path+local_hosts, 'r',encoding='utf-8') as f_hosts, open(hosts_path+gray_hosts, 'w',encoding='utf-8') as f_new_gray, open(hosts_path+'grayHosts.txt', 'r',encoding='utf-8') as tem_gray:
            for txt in f_hosts:f_new_gray.write(txt)
            f_new_gray.write("\n\n")
            for txt in tem_gray:f_new_gray.write(txt)
        print("初始化完毕")

    if type=="toGray":
        with open(path+local_hosts, 'w',encoding='utf-8') as f_hosts, open(hosts_path+gray_hosts, 'r',encoding='utf-8') as f_gray:
            f_hosts.seek(0)
            f_hosts.truncate()
            for txt in f_gray:f_hosts.write(txt)
            return "now is gray"
    else:
        with open(path+local_hosts, 'w',encoding='utf-8') as f_hosts, open(hosts_path+original_hosts, 'r',encoding='utf-8') as f_original:
            f_hosts.seek(0)
            f_hosts.truncate()
            for txt in f_original:f_hosts.write(txt)
            return "now is pro"


if __name__ == "__main__":
    print(editHosts("toGray"))
    print(editHosts("toPro"))
