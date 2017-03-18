# -*-coding:utf-8-*-


# # set oracle ipaddress, port, sid, account, password
# ipaddres : port -> key
ORACLE_ACCOUNT = {
    # oracle
    # "127.0.0.1:1521": ["cedb", "system", "password"]
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
MONGO_USER = "sqlreview"
MONGO_PASSWORD = "sqlreview"
MONGO_DB = "sqlreview"

# server port setting
SERVER_PORT = 7000

# capture time setting
CAPTURE_OBJ_HOUR = "18"
CAPTURE_OBJ_MINUTE = 15
CAPTURE_OTHER_HOUR = "18"
CAPTURE_OTHER_MINUTE = 30

