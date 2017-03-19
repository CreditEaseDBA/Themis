## Themis 

### 介绍

Themis，是宜信公司DBA团队开发的一款数据库审核产品。可帮助DBA、开发人员快速发现数据库质量问题，提升工作效率。


### 快速开始  

注：mongo、redis、mysql都需要预先安装，mongo用来存储数据，redis用来作为celery的调度队列，mysql用来存储pt-query-digest的分析结果，如果大家对python不是很熟悉，强烈建议按照下面的步骤安装，关于mongo的启动，在测试环境建议直接使用root用户用mongod启动不要使用认证,生产环境可以加上认证，加上认证后用户连接需要授权，具体的用户授权方式请自行搜索

如果只想针对mysql数据库进行审核请参考dev分支：https://github.com/CreditEaseDBA/Themis/tree/dev

导入规则

    mongoimport -h 127.0.0.1 --port 27017 -d sqlreview -c rule --file script/rule.json
根据实际情况配置账号密码，建议-d选项使用sqlreview,-c使用默认的rule

新建用户

注：下面的操作除了安装virtualenv在root用户下操作，其他都建议在themis-test用户下操作。celery在root用户启动时需要增加特殊配置。

    adduser themis-test
    su - themis-test

下载代码

    git clone https://github.com/CreditEaseDBA/Themis

安装virtualenv最新版[链接](https://pypi.python.org/simple/virtualenv/)

创建虚拟环境：
    
    cd /home/themis-test
    virtualenv python-project --python=python2.7

初始化虚拟环境

    source /home/themis-test/python-project/bin/activate

安装cx_Oracle的依赖项，[参考](http://www.jianshu.com/p/pKz5K7)

安装依赖包：

对于使用python2.6的用户，请安装[importlib-1.0.3.tar.gz](https://pypi.python.org/simple/importlib/)

    tar -zxvf importlib-1.0.3.tar.gz
    cd importlib-1.0.3
    python setup.py install

安装其他依赖：
    
    cd /home/themis-test/Themis
    pip install -r requirement.txt

单独安装PyH==0.1，参考[PyH](https://github.com/hanxiaomax/pyh)

    unzip pyh-master.zip
    cd pyh-master
    python setup.py install


配置settings.py文件包括oracle、mysql、redis、mongo、pt-query-digest存储数据的帐号密码

配置mongo
    
    MONGO_SERVER = "127.0.0.1"
    MONGO_PORT = 27017
    MONGO_USER = ""
    MONGO_PASSWORD = ""
    MONGO_DB = "sqlreview"


运行命令

    cd /home/themis-test/Themis
    supervisord -c script/supervisord.conf

访问 http://ip:7000/ 是审核平台的管理页面，在这里暂时只能对对象类规则进行审核，其他类规则需要采集数据后才可以进行审核。

注：
针对上面安装virtualenv和依赖包时网络不通的情况可以从[此处下载](https://pan.baidu.com/s/1o7AIWlG),提取码 3sy3，下载后解压然后运行下面的命令安装依赖包

    pip install --no-index -f file:///home/themis-test/software -r requirement.txt

file:///home/themis-test/software指定安装包的位置

如有问题可以参考: https://tuteng.gitbooks.io/themis/content/chang-jian-wen-ti.html

### WIKI

https://tuteng.gitbooks.io/themis/content/ 

正在完善

### 联系方式

EMail：
    sqlreview_themis@126.com

微信群：

![微信](data/img/weixin.png)

qq群：

![qq](data/img/qq.png)
