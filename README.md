## Themis 

### 介绍

Themis，是宜信公司DBA团队开发的一款数据库审核产品。可帮助DBA、开发人员快速发现数据库质量问题，提升工作效率。


### 快速开始  

导入规则

    mongoimport -h 127.0.0.1 --port 27017 -u sqlreview -p password -d sqlreview -c rule --file script/rule.json
根据实际情况配置账号密码，建议-d选项使用sqlreview

新建用户

    adduser themis-test
    su - themis-test

下载代码

    git clone https://github.com/CreditEaseDBA/Themis

安装virtualenv最新版[链接](https://pypi.python.org/simple/virtualenv/)

创建虚拟环境：

    virtualenv python-project --python=python2.7

初始化虚拟环境

    source /home/themis-test/python-project/bin/activate

安装cx_Oracle的依赖项，[参考](http://www.jianshu.com/p/pKz5K7)

安装依赖包：
    
    cd /home/themis-test/themis
    pip install -r requirement.txt

单独安装PyH==0.1，参考[PyH](https://github.com/hanxiaomax/pyh)

    unzip pyh-master.zip
    cd pyh-master
    python setup.py install


配置settings.py文件包括oracle、mysql、redis、mongo、pt-query-digest存储数据的帐号密码


运行命令

    cd /home/themis-test/themis
    supervisord -c script/supervisord.conf

访问 http://ip:7000/ 是审核平台的管理页面

注：
针对上面安装virtualenv和依赖包时网络不通的情况可以从[此处下载](https://pan.baidu.com/s/1o7AIWlG),提取码 3sy3，下载后解压然后运行下面的命令安装依赖包

    pip install --no-index -f file:///home/themis-test/software -r requirement.txt

file:///home/themis-test/software指定安装包的位置

### WIKI
临时可参考：sqlreview.md，更详细的文档正在完善中  

正在完善

### 联系方式

EMail：
    sqlreview_themis@126.com

微信群：

![微信](data/img/weixin.png)

qq群：

![qq](data/img/qq.png)
