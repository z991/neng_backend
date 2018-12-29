"""
function：基础公用方法
describe：基础公用操作方法封装
date：20171127
author：gjf
version:1.09
"""
import logging
import hashlib
import re
from django.conf import settings
from libs.hash import decrypt
from libs.classic_service.mysqldbhelper import MysqldbHelper
logger = logging.getLogger('django')
"""
function:ali_dbcon_kf
describe:获取阿里云数据库连接
return: bool or pymysql.cursors.Cursor
"""
def ali_dbcon_kf(dbname):
    try:
        # oa数据库信息
        oa_dbhost = 'rdsrypnu7hzxe7f5iwdt7public.mysql.rds.aliyuncs.com'
        oa_dbuser = 'ntreaderv'
        oa_dbpwd = '8qrl177!'
        oa_dbname = dbname
        oa_port = 3306
        oa_dbcon = MysqldbHelper(oa_dbhost, oa_dbuser, oa_dbpwd, oa_dbname, oa_port)
        if oa_dbcon == False:
            return False
        return oa_dbcon
    except Exception as e:
        logger.error(e)
        return False
"""
function:dbcon_oa
describe:获取oa数据库连接
return: bool or pymysql.cursors.Cursor
"""
def dbcon_oa():
    try:
        # oa数据库信息
        oa_dbhost = settings.DATABASES['default']['HOST']
        oa_dbuser = settings.DATABASES['default']['USER']
        oa_dbpwd = settings.DATABASES['default']['PASSWORD']
        oa_dbname = settings.DATABASES['default']['NAME']
        oa_port = settings.DATABASES['default']['PORT']
        oa_dbcon = MysqldbHelper(oa_dbhost, oa_dbuser, oa_dbpwd, oa_dbname, int(oa_port))
        if oa_dbcon == False:
            return False
        return oa_dbcon
    except Exception as e:
        logger.error(e)
        return False
"""
function:md5Encode
describe:解密
return: string
"""
def md5Encode(string):
    m = hashlib.md5(string.encode("utf-8"))
    return m.hexdigest()
def checkversion(siteid):
    data=re.match(r'^[a-zA-Z]+_\d+',siteid)
    if data is None:
        return False
    if siteid.split('_')[0] != 'kf' and int(siteid.split('_')[1]) == 1000:
        return 'b2b'
    elif siteid.split('_')[0] == 'kf':
        return 'b2c'
    elif siteid.split('_')[0] !='kf':
        return 'b2b2c'
    else:
        return False