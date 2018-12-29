import time
import datetime
from operator import itemgetter
import redis
from libs.mysql_base import MysqldbHelper
from libs.hash import decrypt
from django.conf import settings
from libs.redis import Redis_base


class ClasicData:

    def __init__(self):
        self.oa_db = self.get_db_con_oa()

    def logic(self):
        starttime_ing = (int(time.mktime(time.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')))-24*60*60)*1000
        starttime = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d')+' 00:00:00', '%Y-%m-%d %H:%M:%S')))*1000
        endtime = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d')+' 23:59:59', '%Y-%m-%d %H:%M:%S')))*1000
        ret = self.get_grid_dbcon()
        _ret = []
        consult_num_total,consulting_num_total = 0,0
        visitor_num_total = 0
        _letao_address_list = []

        for k in ret:
            consult_num,consulting = 0,0
            db_address = k['db_address']
            db_username = k['db_username']
            db_pwd = k['db_pwd']
            db_port = k['db_port']
            if k['db_name'] == 'kf':
                try:
                    db_name = 'kf'
                    dbcon_kf = MysqldbHelper(db_address, db_username, decrypt(db_pwd), db_name, int(db_port))
                    if dbcon_kf == False:
                        continue
                    sql = f"SELECT count(*) as num from t2d_chatscene where starttime>={starttime} and endtime<={endtime}"
                    consult = dbcon_kf.select(sql)
                    consult_num_total = int(consult_num_total + consult[0]['num'])
                    consult_num = consult[0]['num']
                    sql = f"SELECT count(*) as num from t2d_chatscene where starttime>={starttime_ing} and endtime=0"
                    consulting = dbcon_kf.select(sql)
                    consulting_num_total = int(consulting_num_total + consulting[0]['num'])
                except:
                    continue
            elif k['db_name'] == 'letaotrailcenter':
                try:
                    if _letao_address_list.count(db_address)>0:
                        continue
                    db_name = 'letaotrailcenter'
                    dbcon_letao = MysqldbHelper(db_address, db_username, decrypt(db_pwd), db_name, int(db_port))
                    if dbcon_letao == False:
                        continue
                    date = time.strftime('%Y%m%d')
                    sql = f'select table_name from information_schema.tables where table_name LIKE "t2d_%_ip_hits_{date}"'
                    table_name = dbcon_letao.select(sql)
                    visitor_num = 0
                    for key in table_name:
                        sql = f"select count(*) as num from {key['table_name']}"
                        visitor = dbcon_letao.select(sql)
                        visitor_num = int(visitor_num+visitor[0]['num'])
                    visitor_num_total = visitor_num_total+visitor_num
                    _letao_address_list.append(db_address)
                except:
                    continue
            else:
                continue

            if consult_num>=25000:
                state = "灾难"
            elif consult_num>=18000:
                state = "告警"
            else:
                state = "正常"
            strr = {"grid_name": k['grid_name'], "consult_num": consult_num,"threshold":18000,"state":state}
            _ret.append(strr)
        # redis存入正在咨询量
        consulting_str = f"{time.strftime('%H:%M:%S')}|{consulting_num_total}"
        consulting_key = "consulting"+time.strftime('%Y%m%d')
        yest_consulting_key = "consulting"+(datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y%m%d')
        if Redis_base().exists(yest_consulting_key):
            Redis_base().delete(yest_consulting_key)
        Redis_base().lpush(consulting_key, consulting_str)
        consulting_json = []
        consulting_len = Redis_base().llen(consulting_key)
        for k in range(consulting_len):
            try:
                data = Redis_base().lindex(consulting_key, k)
                if data:
                    data_lsit = str(data).split('|')
                    data_dict = {data_lsit[0]: data_lsit[1]}
                    consulting_json.append(data_dict)
            except:
                consulting_json = consulting_json
        sorted_ret = sorted(_ret, key=lambda _ret: _ret['consult_num'],reverse=True)
        ret_str = {"consult":{"total":consult_num_total,"grid_num":sorted_ret},"visitor":{"total":visitor_num_total},"consulting":consulting_json}
        Redis_base().set("classic_gjf", ret_str)
        return ret_str
    def get_db_con_oa(self):
        try:
            # oa数据库信息
            oa_dbhost = settings.DATABASES['default']['HOST']
            oa_dbuser = settings.DATABASES['default']['USER']
            oa_dbpwd = settings.DATABASES['default']['PASSWORD']
            oa_dbname = settings.DATABASES['default']['NAME']
            oa_port = int(settings.DATABASES['default']['PORT'])
            oa_dbcon = MysqldbHelper(oa_dbhost, oa_dbuser, oa_dbpwd, oa_dbname, oa_port)
            if oa_dbcon == False:
                return False
            return oa_dbcon
        except Exception as e:
            return False
    def get_grid_dbcon(self):
        try:
            sql = "select a.db_address,a.db_name,a.db_username,a.db_pwd,a.db_port,a.grid_id,b.grid_name from production_manage_databaseinfo as a LEFT JOIN production_manage_grid as b ON a.grid_id=b.id"
            ret = self.oa_db.select(sql)
            return ret
        except:
            return False


