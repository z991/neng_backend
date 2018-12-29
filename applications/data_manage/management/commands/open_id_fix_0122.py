# __author__ = gzh

from django.core.management import BaseCommand

from applications.data_manage.models import InquiriesData
from applications.workorder_manage.models import OpenStationManage
from ldap_server.configs import CHANNEL_PC


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        author: gzh
        function: 为没有open_id的InquiriesData写入open_id;
                纠正channel为0的InquiriesData的channel为6
        param args: None
        param options: None
        return: None
        """
        sites = OpenStationManage.objects.all()
        site_open_map = {}
        for site in sites:
            site_id = site.station_info.company_id
            open_id = site.id
            site_open_map[site_id] = open_id

        # 修复已有咨询量数据中的open_id字段信息 和 渠道为CHANNEL_PC 的 代码为 6
        for data in InquiriesData.objects.all():
            if data.company_id in site_open_map.keys():
                data.open_id = site_open_map[data.company_id]

            if data.channel == 0:
                data.channel = CHANNEL_PC
            data.save()


