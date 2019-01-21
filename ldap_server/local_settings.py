import os

# Site Config
BASE_URL = "http://127.0.0.1:8000"
SECRET_KEY = "t8w!2mju@sd9_)*xh*cp7$f-mdpymmr=l!oa0u_nb9l*s)eh!7"
DEBUG = True

# DB Config
DB_HOST = '127.0.0.1'
DB_NAME = 'oa_backend'
DB_PASSWORD = '111111'
DB_PORT = '3306'
DB_USER = 'root'

# 客服路由数据库地址
CUSTORM_DATABASE = os.environ.get("CUSTORM_DATABASE")
CUSTORM_HOST = os.environ.get("CUSTORM_HOST")
CUSTORM_PORT = int(os.environ.get("CUSTORM_PORT", 0))
CUSTORM_USER = os.environ.get("CUSTORM_USER")
CUSTORM_PASSWORD = os.environ.get("CUSTORM_PASSWORD")


# zabbix接口url
ZABBIX_URL = os.environ.get("ZABBIX_URL")
# zabbix用户名
ZABBIX_USER = os.environ.get("ZABBIX_USER")
ZABBIX_PASSWORD = os.environ.get("ZABBIX_PASSWORD")


# 重构postgres数据库
REFACTOR_HOST = os.environ.get("REFACTOR_HOST")
REFACTOR_DATABASE = os.environ.get("REFACTOR_DATABASE")
REFACTOR_USER = os.environ.get("REFACTOR_USER")
REFACTOR_PASSWORD = os.environ.get("REFACTOR_PASSWORD")
REFACTOR_PORT = int(os.environ.get("REFACTOR_PORT", 0))


# powerdog数据库
POWERDOG_DB_HOST = os.environ.get("POWERDOG_DB_HOST")
POWERDOG_DB_NAME = os.environ.get("POWERDOG_DB_NAME")
POWERDOG_DB_USER = os.environ.get("POWERDOG_DB_USER")
POWERDOG_DB_PASSWORD = os.environ.get("POWERDOG_DB_PASSWORD")
POWERDOG_DB_PORT = int(os.environ.get("POWERDOG_DB_PORT", 0))


# influx数据库
INFLUX_HOST = os.environ.get("INFLUX_HOST")
INFLUX_DATABASE = os.environ.get("INFLUX_DATABASE")
INFLUX_USER = os.environ.get("INFLUX_USER")
INFLUX_PASSWORD = os.environ.get("INFLUX_PASSWORD")
INFLUX_PORT = os.environ.get("INFLUX_PORT")

# Redis Config
REDIS_DBNUM = 0
REDIS_PORT = 6379
REDIS_PASSWORD = ""
REDIS_SERVER = "redis"

