from urllib import parse

from django.core.management import BaseCommand

from applications.data_manage.models import InquiriesData
from applications.production_manage.models import DataBaseInfo, ServerGroup
from applications.workorder_manage.models import OpenStationManage, StationInfo
from libs.hash import decrypt
from libs.mysql_helper import Connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 连接池
        conn_poll = {}
        for db_info in DataBaseInfo.objects.all().filter(db_name='kf'):
            try:
                print(db_info.db_address)
                conn = Connection(database=db_info.db_name,
                                  host=db_info.db_address,
                                  port=int(db_info.db_port),
                                  user=db_info.db_username,
                                  password=decrypt(db_info.db_pwd))
                conn_poll[db_info.db_address] = conn
            except:
                print(db_info.db_name)
                print(db_info.db_address)
                continue

        sites = OpenStationManage.objects.all()
        for site in sites:
            try:
                print(site.station_info.company_id)
                site_id = site.station_info.company_id
                db_host = site.station_info.grid.db_info.get(db_name="kf").db_address
                conn = conn_poll[db_host]
                res = conn.get(
                    "select t2dserver from t_wdk_sit where sitid = '%s'" % site_id)
                if res:
                    grp_name = parse.urlparse(res.t2dserver).netloc.split("-in")[0]
                    site.station_info.server_grp = ServerGroup.objects.get(
                        group_name__contains=grp_name)
                    site.station_info.save()
            except:
                print('error:'+site.station_info.company_id)
                continue
        for conn in conn_poll.values():
            conn.close()

        # 修复已有咨询量数据中的servergroup字段信息
        site_id_server_grp_ship = dict(StationInfo.objects.all().values_list("company_id", "server_grp__group_name"))
        for data in InquiriesData.objects.all():
            try:
                data.server_grp = site_id_server_grp_ship[data.company_id]
                data.save()
            except:
                print('error:'+data.company_id)
                continue
