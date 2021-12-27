# 基于的基础镜像
FROM python:3.7

# 维护者信息
MAINTAINER xuwei.fan

# 设置code文件夹是工作目录
WORKDIR /icode_test_platform

COPY requirements.txt ./
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
COPY . .

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN sed -i s@/security.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update
# RUN apt-get -y install vim
RUN apt-get -y install cron
RUN service cron start

# 调整时区
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN python /icode_test_platform/conf/initCron.py

CMD ["gunicorn", "app:app", "-c", "./gunicorn.conf.py"]