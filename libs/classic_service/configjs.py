"""
function：Configjs操作类
describe：Configjs操作类封装
date：20171127
author：gjf
version:1.09
"""
# coding=utf-8
import time
class Configjs:
    """
    function:__init__
    describe:构造函数初始连接数据库kf库
    param: pymysql.cursors.Cursor @dbcon kf库
    return: json
    """
    def __init__(self, dbcon):
        self.dbcon = dbcon

    """
    function:configjs
    describe:修改configjs操作表
    param: string @siteid 企业id
    param: string @settingid 接待组id
    return: json
    """
    def configjs(self, siteid, settingid=None):
        updatetime = int(time.time())
        if settingid:
            sql = "update t2d_syssetting set updatetime = %d where siteid = '%s' and id = '%s'" % \
                  (updatetime, siteid, settingid)
        else:
            sql = "update t2d_syssetting set updatetime = %d where siteid = '%s'" % \
                  (updatetime, siteid)
        data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False
