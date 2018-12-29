# __author__ = itsneo1990
from urllib import parse

from django.core.management import BaseCommand

from applications.production_manage.models import FunctionInfo, VersionInfo
from libs.mysql_helper import Connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 连接
        conn = Connection(database='oa_platform',
                          host='192.168.30.98',
                          port=3306,
                          user='root',
                          password='tYhep69NeUckDNLnCgxs')

        functions = FunctionInfo.objects.all()
        func_version_map = {}
        for func in functions:
            res = conn.get(
                "select product_id, id from production_manage_versioninfo where id =" \
                "(SELECT version_id from production_manage_functioninfo where id = %d)" % func.id)
            if res:
                # 为已有function写入product_id
                func.product_id = int(res.product_id)
                func.save()
                func_version_map.setdefault(func.id, [])
                func_version_map[func.id].append(res.id)

        conn.close()

        # 为已有function写入对应的version
        for func in functions:
            if func.id in func_version_map.keys():
                version_set = VersionInfo.objects.all().filter(id__in=func_version_map[func.id])
                func.version.set(version_set)
                func.save()
