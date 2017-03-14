### 采集数据： 
#### mysql部分： 
pt-query-digest使用 
1. 可以将慢日志集中到一个地方，再集中入库 
2. 也可以在每台mysql机器上安装pt-query-digest,再将解析结果推送到存储机器上 
本平台采用第二种方案 
首先安装mysql 
从https://www.percona.com/get/pt-query-digest下载并安装pt-query-digest，如果缺少依赖使用yum安装
使用scirpt/pt_query_digest.sql初始化表结构,不要使用默认的表结构 
在目标机器上配置好pt-query-digest.sh脚本，主要是配置存储解析结果的mysql机器的帐号，密码，机器ip，端口号，以及慢日志的位置等。 
运行pt-query-digest.sh脚本开始搜集mysql慢查询数据，后面可以将其加入定时任务，按固定时间段搜集。 

#### oracle部分： 
下载mongodb，安装mongodb，用来存储规则和抓取的数据，执行的任务等 
配置mongodb具有eval执行权限，参考：http://www.cnblogs.com/viewcozy/p/4683666.html
在settings.py文件中配置好ORACLE_ACCOUNT，将要采集数据的目标机器的ip，端口，帐号，密码，sid等配置好，并在目标机器上开通帐号权限。
连接oracle目标库统一采用sid的方式 
使用 python command.py -m capture -t data/capture_obj.json 运行采集对象命令  
使用 python command.py -m capture -t data/capture_other.json 采集其他信息 
将这两部分分开主要是因为，这两个采集模块比较耗时，将来可以放在celery的不同队列里 
-t指定任务类型，分为四部分capture，analysis，export，web 
-c指定配置文件，在data目录下有相应的模版 
找一台线下的机器，看看线下有哪些库需要做审核，进行一些相应的配置，搭建环境，记录文档 

简单安装步骤：
首先导入规则
mongoimport -d sqlreview -c rule --file script/rule.json

配置settings.py文件，包括需要审核的目标oracle机器的帐号、密码，mysql机器的帐号、密码，pt-query存储结果的帐号、密码，mongo的帐号、密码，redis的连接方式等

接着初始化数据：
初始化mysql数据，
1.初始化表结构使用脚本script/pt-query-digest.sql
2.初始化慢查询数据使用脚本script/pt-query-digest.sh，需配置存储结果的机器的帐号和密码，以及slow_log的位置等

初始化oracle数据：
配置data/capture_other.json文件
{
    "module": "capture",
    "type": "OTHER",
    "db_type": "O",
    "db_server": "127.0.0.1",
    "db_port": 1521,
    "capture_date": "2017-02-28"
}
使用 python command.py -m capture_other -c data/capture_other.json 命令
和 python command.py -m capture_obj -c data/capture_obj.json 命令
需要配置采集数据机器的ip地址，后面可以使用celery配合supervisor定时采集


手动解析规则：
python command.py -m analysis_m_obj -c data/analysis_m_obj.json 
python command.py -m analysis_m_text -c data/analysis_m_text.json
python command.py -m analysis_m_plan -c data/analysis_m_plan.json
python command.py -m analysis_m_stat -c data/analysis_m_stat.json

python command.py -m analysis_o_obj -c data/analysis_o_obj.json
python command.py -m analysis_o_plan -c data/analysis_o_plan.json
python command.py -m analysis_o_stat -c data/analysis_o_stat.json
python command.py -m analysis_o_text -c data/analysis_o_text.json


手动开启web管理：
python command.py -m web -c data/web.json
端口号：7000

手动导出任务：
python command.py -m export -c data/export.json
端口号：9000

通过supervisor进行任务管理
见配置文件script/supervisord.conf

flower平台端口：5555

部署安装常见问题：
主机名称不一致，导致cx_Oracle出错
celery与flower版本不一致，导致flower不能启动，升级flower到0.8.1以上
mysql5.7不能初始化datetime默认类型为(DEFAULT '0000-00-00 00:00:00)
mongodb文档最大插入数据有限制，最大多少需测试
在oracle获取用户的时候，可能会将用户建到users下，因此需要将 NOT IN ('USERS', 'SYSAUX'))改成 NOT IN ('SYSAUX'))


#### 导入规则

    mongoimport -d sqlreview -c rule --file script/rule.json

#### 配置settings.py文件

    # set oracle ipaddress, port, sid, account, password
    # ipaddres : port -> key
    ORACLE_ACCOUNT = {
        "127.0.0.1:1521": ["cedb", "system", "password"]
    }
    
    # set mysql ipaddress, port, account, password
    MYSQL_ACCOUNT = {
        "127.0.0.1:3307": ["mysql", "user", "password"]
    }
    
    # pt-query save data for mysql account, password
    PT_QUERY_USER = "user"
    PT_QUERY_PORT = 3306
    PT_QUERY_SERVER = "127.0.0.1"
    PT_QUERY_PASSWD = "password"
    PT_QUERY_DB = "slow_query_log"
    
    # celery setting
    REDIS_BROKER = 'redis://:password@127.0.0.1:6379/0'
    
    REDIS_BACKEND = 'redis://:password@127.0.0.1:6379/0'
    
    CELERY_CONF = {
        "CELERYD_POOL_RESTARTS": True
    }
    
    # mongo server settings
    MONGO_SERVER = "127.0.0.1"
    MONGO_PORT = 27017
    MONGO_USER = ""
    MONGO_PASSWORD = ""
    MONGO_DB = "sqlreview"
    
    # server port setting
    SERVER_PORT = 7000
    
    # capture time setting
    CAPTURE_OBJ_HOUR = "18"
    CAPTURE_OBJ_MINUTE = 15
    CAPTURE_OTHER_HOUR = "18"
    CAPTURE_OTHER_MINUTE = 30

按照上面的配置模版进行配置，配置oracle的ip地址、端口、帐号、密码、sid，配置mysql的ip地址、端口、帐号、密码，多台机器使用列表分开，配置mongo的主机、端口、帐号、密码、存储规则集的库名称等，配置web管理端开启口监听的端口号，配置数据采集的时间等。

#### 初始化数据
##### 初始化mysql数据
1.初始化表结构使用脚本script/pt-query-digest.sql
2.初始化慢查询数据使用脚本script/pt-query-digest.sh，需配置存储结果的机器的帐号和密码，以及slow_log的位置等

##### 初始化oracle数据

###### 手动采集plan、stat、text数据
配置data/capture_other.json文件

    {
        "module": "capture",
        "type": "OTHER",
        "db_type": "O",
        "db_server": "127.0.0.1",
        "db_port": 1521,
        "capture_date": "2017-02-28"
    }

只需要配置db_server、db_port、capture_date三个选项就可以了，此处的db_server、db_port必须在上面的settings.py中已经进行过配置

    python command.py -m capture_other -c data/capture_other.json
使用上面命令开始采集数据

###### 手动采集obj数据
配置data/capture_obj.json文件

    {
        "module": "capture",
        "type": "OBJ",
        "db_type": "O",
        "db_server": "127.0.0.1",
        "db_port": 1521,
        "capture_date": "2017-02-28"
    }
配置方法同上面

    python command.py -m capture_obj -c data/capture_obj.json
使用上面的命令开始采集obj数据

#### 自动采集数据
在settings.py
需要配置采集数据机器的ip地址，后面可以使用celery配合supervisor定时采集。

#### 规则解析
规则解析根据数据库类型分为oracle和mysql，根据规则类型分为obj，text，plan和stat，根据复杂度分为简单规则和复杂规则，下面以oracle和mysql的plan规则来说明一下如何手动进行规则解析

##### oracle plan类型规则解析
配置data/oracle_o_plan.json文件

    {
        "module": "analysis",
        "type": "SQLPLAN",
        "capture_date": "2017-02-23",
        "username": "schema",
        "create_user": "SYSTEM",
        "sid": "cedb",
        "db_type": "O",
        "rule_type": "SQLPLAN",
        "rule_status": "ON",
        "task_ip": "127.0.0.1",
        "task_port": 1521
    }
    
主要是对type,capture_date,username, create_user, sid,db_type,rule_type,task_ip,task_port参数进行配置，type分为SQLPLAN,SQLSTAT,TEXT,OBJ四种类型，rule_type的类型同type，只不过一个是代表模块的类型，一个代表规则的类型，db_type分为"O"和“mysql”两种类型，分别代表oracle和mysql，capture_date为数据的抓取日期

    python command.py -m analysis -c data/analysis_o_plan.json
运行上面的命令即可生成解析结果

##### mysql plan规则解析
配置data/analysis_m_plan.json文件

    {
        "module": "analysis",
        "type": "SQLPLAN",
        "hostname_max": "127.0.0.1:3306",
        "db_server": "127.0.0.1",
        "db_port": 3306,
        "username": "schema",
        "db_type": "mysql",
        "rule_status": "ON",
        "create_user": "mysqluser",
        "task_ip": "127.0.0.1",
        "rule_type": "SQLPLAN",
        "task_port": 3306,
        "startdate": "2017-02-21 00:00:00",
        "stopdate": "2017-02-22 23:59:00"
    }
type类型的含义同上面oracle，hostname_max为mysql的ip:端口号的形式，每一个hostname_max代表一个mysql实例，startdate和stopdate需要加上时、分、秒，这一点同oracle不大一样

    python command.py -m analysis -c data/analysis_m_plan.json
然后运行上面的命令进行mysql的plan的规则解析

##### 其他规则解析
其他的规则就和上面的oracle和mysql的规则解析类似，在data文件加下都有相应的模版，运行如下命令进行规则解析

    # 解析mysql的obj类型
    python command.py -m analysis_m_obj -c data/analysis_m_obj.json
    # 解析mysql的text类型
    python command.py -m analysis_m_text -c data/analysis_m_text.json
    # 解析mysql的plan类型
    python command.py -m analysis_m_plan -c data/analysis_m_plan.json
    # 解析mysql的stat类型
    python command.py -m analysis_m_stat -c data/analysis_m_stat.json
    # 解析oracle的obj类型
    python command.py -m analysis_o_obj -c data/analysis_o_obj.json
    # 解析oracle的plan类型
    python command.py -m analysis_o_plan -c data/analysis_o_plan.json
    # 解析oracle的stat类型
    python command.py -m analysis_o_stat -c data/analysis_o_stat.json
    # 解析oracle的text类型
    python command.py -m analysis_o_text -c data/analysis_o_text.json
    
#### 自动规则解析
在这里自动规则解析我们使用了celery来完成，关于celery 的使用，请参考[celery使用说明](http://docs.celeryproject.org/en/master/getting-started/first-steps-with-celery.html)

当然为了查看任务状态，我们可以借助于celery的web端管理工具[flower](https://flower.readthedocs.io/en/latest/)

    celery flower --address=0.0.0.0 --broker=redis://:password@127.0.0.1:6379/0
运行上面的命令将flower开启,然后访问127.0.0.1:5000即可看到当前的任务状态

#### 规则导出

##### 手动导出报告
配置data/export.json文件

    {
        "module": "export",
        "type": "export",
        "task_uuid": "08d03ec6-f80a-11e6-adbc-005056a30561",
        "file_id": "08d03ec6-f80a-11e6-adbc-005056a30561"
    }
需要填写task_uuid和file_id，task_uuid是我们刚才进行规则解析时生成的任务id，可以从mongo中查看，也可以通过脚本输出，file_id为我们要导出报告时生成的报告压缩包的名称，这里我们和task_uuid保持一致。

    python command.py -m export -c data/export.json
运行上面的命令可以生成报告，报告保存在task_export/downloads文件夹下，可以直接复制出来，建议用chrome或firefox浏览器打开，进行分析

##### 自动导出报告
这种方式基本上是我们环境部署好之后经常使用的。
为了将报告从服务器上拉下来，我们开发了一个简单的文件下载服务器，当我们通过celery异步生成报告之后我们变可以通过文件下载服务器将报告下载下来，或者将报告链接发送给其他人

##### web管理端
为了对规则进行管理，对解析结果展示，分析，我们开发了一个简单的web端。

    python command.py -m web -c data/web.json
运行这个命令可以将服务开起来
通过使用 127.0.0.1:7000 访问服务
