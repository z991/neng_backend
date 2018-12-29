"""
function：Jms jms操作类
describe：jms操作类封装
date：20171127
author：gjf
version:1.09
"""
# coding=utf-8
import requests
import logging
logger = logging.getLogger('django')
class Jms:
    """
    function:__init__
    describe:构造函数初始连接数据库kf库
    param: pymysql.cursors.Cursor @dbcon kf库
    return: json
    """
    def __init__(self, dbcon):
        self.dbcon = dbcon

    """
    function:sendjms
    describe:发送jms
    param: string @siteid 企业id
    param: array @post_data post需传送的参数
    return: json
    """
    def sendjms(self, siteid, post_data):
        headers = {'Content-Type': 'application/json'}
        sql = "SELECT `tstatusserver` FROM `t_wdk_sit` t WHERE sitid='%s'" % (siteid)
        data = self.dbcon.select(sql)
        if data:
            jmsUrl = data['tstatusserver']
        else:
            logger.info('jms查询数据表配置为空')
            return {'status': False, 'error': sql}
        url = "%s/tstatus/webevent?" % (jmsUrl)
        result = requests.post(url, headers=headers, data=post_data)
        result_json = result.json()
        if result_json['status'] == 1:
            logger.info('jms发送成功')
            return {'status': True, 'error': 'null'}
        else:
            logger.info('jms发送失败')
            return {'status': False, 'error': url}
