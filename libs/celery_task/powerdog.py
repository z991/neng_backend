import time
from libs.mysql_base import MysqldbHelper
from ldap_server.database_connect import POWERDOG_HOST, POWERDOG_NAME, POWERDOG_PASSWORD, POWERDOG_PORT, POWERDOG_USER
from libs.redis import Redis_base


class PowerDog:

    def __init__(self):
        self.powerdog_db = self.get_db_con_prowerdog()

    def logic(self):
        try:
            table = "monitor_result_"+time.strftime('%Y_%m_%d')
            sql = "select * from "+table+" where time>=now()-interval 5 minute GROUP BY taskId ORDER BY time DESC"
            data = self.powerdog_db.select(sql)
            ret = []
            for k in data:
                str = {}
                if k['pingTrailServer'] == 0:
                    str = {"taskId":k['taskId'],"error":"轨迹网络异常","time":k['time']}
                elif k['pingGetFlashServer'] == 0:
                    str = {"taskId": k['taskId'], "error": "FlashServer网络异常", "time": k['time']}
                elif k['getServerAddr'] == 0:
                    str = {"taskId": k['taskId'], "error": "ServerAddr异常", "time": k['time']}
                elif k['webTrail'] == 0:
                    str = {"taskId": k['taskId'], "error": "用户轨迹异常", "time": k['time']}
                elif k['kfConnectT2d'] == 0:
                    str = {"taskId": k['taskId'], "error": "客服连接异常", "time": k['time']}
                elif k['kfLoginT2d'] == 0:
                    str = {"taskId": k['taskId'], "error": "客服登录异常", "time": k['time']}
                elif k['visitorRequestKf'] == 0:
                    str = {"taskId": k['taskId'], "error": "访客请求失败", "time": k['time']}
                elif k['visitorConnectTchat'] == 0:
                    str = {"taskId": k['taskId'], "error": "访客连接失败", "time": k['time']}
                elif k['kfConnectTchat'] == 0:
                    str = {"taskId": k['taskId'], "error": "客服会话失败", "time": k['time']}
                elif k['uploadFile'] == 0:
                    str = {"taskId": k['taskId'], "error": "文件上传失败", "time": k['time']}
                elif k['downloadFile'] == 0:
                    str = {"taskId": k['taskId'], "error": "文件下载失败", "time": k['time']}
                ret.append(str)
        except:
            ret = []
        Redis_base().set("power_dog0829", ret)
        return ret

    def get_db_con_prowerdog(self):
        try:
            # POWERDOG数据库信息
            powerdog_dbhost = POWERDOG_HOST
            powerdog_dbuser = POWERDOG_USER
            powerdog_dbpwd = POWERDOG_PASSWORD
            powerdog_dbname = POWERDOG_NAME
            powerdog_port = POWERDOG_PORT
            powerdog_dbcon = MysqldbHelper(powerdog_dbhost, powerdog_dbuser, powerdog_dbpwd, powerdog_dbname, powerdog_port)
            if powerdog_dbcon == False:
                return False
            return powerdog_dbcon
        except Exception as e:
            return False



