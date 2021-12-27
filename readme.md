# 豌豆编程测试平台

### 下拉项目文件
```shell
git clone https://gz-gitlab.vipthink.cn/xuwei.fan/icode_test_platform.git
```

### 配置文件
调整账号、中间件、环境配置
```shell
vim ~/icode_test_platform/conf/config.ini
```


### Linux部署快速部署
```shell
sudo curl -sSL https://raw.githubusercontent.com/PolkFan/icode_test_platform/master/quick_start.sh | sh
```


### 本地调试 
Python版本：建议Python3.7或以上

执行 `pip3 install -r requirements.txt` 安装依赖

```python
pip3 install -r /icode_test_platform/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

配置文件：conf/config.ini

调试启动Flask项目：python3 -m flask run --host=0.0.0.0 --port=5000

如果遇到`No module named '_ssl'`问题
```shell
# CentOS 操作系统
yum install -y zlib zlib-dev openssl-devel sqlite-devel bzip2-devel libffi libffi-devel gcc gcc-c++
wget http://www.openssl.org/source/openssl-1.1.1.tar.gz
tar -zxvf openssl-1.1.1.tar.gz
cd openssl-1.1.1
./config --prefix=/usr/local/openssl-1.1.1
make && make install

#echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/openssl/lib" >> $HOME/.bash_profile
#source $HOME/.bash_profile

#wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz
#tar -zxvf Python-3.7.12.tgz
./configure --prefix=/usr/local/python3 --with-openssl=/usr/local/openssl-1.1.1
make && make install
```# icode_test_platform
