import os

from libs.environment import ENV
os.environ['DJANGO_SETTINGS_MODULE'] = 'ldap_server.settings'
from ldap_server.ldap_config import auth_ldap_bind_dn, auth_ldap_bind_password, login_model, ldap_name
current_env = ENV()

if login_model == 2:
    DATABASE = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': current_env.get_config("DB_HOST"),
            'NAME': current_env.get_config("DB_NAME"),
            'USER': current_env.get_config("DB_USER"),
            'PASSWORD': current_env.get_config("DB_PASSWORD"),
            'PORT': current_env.get_config("DB_PORT")
        }
    }
else:
    DATABASE = {
        'ldap': {
            'ENGINE': 'ldapdb.backends.ldap',
            'NAME': ldap_name,
            'USER': auth_ldap_bind_dn,
            'PASSWORD': auth_ldap_bind_password,
        },
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': current_env.get_config("DB_HOST"),
            'NAME': current_env.get_config("DB_NAME"),
            'USER': current_env.get_config("DB_USER"),
            'PASSWORD': current_env.get_config("DB_PASSWORD"),
            'PORT': current_env.get_config("DB_PORT")
        }
    }


# 客服路由数据库地址
CUSTORM_DATABASE = current_env.get_config("CUSTORM_DATABASE")
CUSTORM_HOST = current_env.get_config("CUSTORM_HOST")
CUSTORM_PORT = int(current_env.get_config("CUSTORM_PORT"))
CUSTORM_USER = current_env.get_config("CUSTORM_USER")
CUSTORM_PASSWORD = current_env.get_config("CUSTORM_PASSWORD")


# zabbix接口url
ZABBIX_URL = current_env.get_config("ZABBIX_URL")
# zabbix用户名
ZABBIX_USER = current_env.get_config("ZABBIX_USER")
ZABBIX_PASSWORD = current_env.get_config("ZABBIX_PASSWORD")


# 重构postgres数据库
REFACTOR_HOST = current_env.get_config("REFACTOR_HOST")
REFACTOR_NAME = current_env.get_config("REFACTOR_DATABASE")
REFACTOR_USER = current_env.get_config("REFACTOR_USER")
REFACTOR_PASSWORD = current_env.get_config("REFACTOR_PASSWORD")
REFACTOR_PORT = int(current_env.get_config("REFACTOR_PORT"))


# powerdog数据库
POWERDOG_HOST = current_env.get_config("POWERDOG_DB_HOST")
POWERDOG_NAME = current_env.get_config("POWERDOG_DB_NAME")
POWERDOG_USER = current_env.get_config("POWERDOG_DB_USER")
POWERDOG_PASSWORD = current_env.get_config("POWERDOG_DB_PASSWORD")
POWERDOG_PORT = int(current_env.get_config("POWERDOG_DB_PORT"))


# influx数据库
INFLUX_HOST = current_env.get_config("INFLUX_HOST")
INFLUX_NAME = current_env.get_config("INFLUX_DATABASE")
INFLUX_USER = current_env.get_config("INFLUX_USER")
INFLUX_PASSWORD = current_env.get_config("INFLUX_PASSWORD")
INFLUX_PORT = current_env.get_config("INFLUX_PORT")