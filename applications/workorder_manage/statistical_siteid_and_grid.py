import re
import csv
import codecs
import datetime

from libs.classic_service.basehelp import ali_dbcon_kf
from libs.classic_service.classic_model import AliModel
from applications.workorder_manage.models import StationInfo

from rest_framework.decorators import list_route, api_view
from rest_framework import viewsets, status
from django.http import HttpResponse

today = datetime.date.today()


class SiteAndGridStatistical(viewsets.GenericViewSet):
    queryset = StationInfo.objects.all()

    def get_ali_site_and_grid(self):
        data = AliModel().get_siteid_routing()
        result = {}
        for item in data:
            old_grid = item['scripturl']
            reps = re.match(r"http://(\w+-\w+)", old_grid, re.I)
            if not reps:
                continue
            grid = reps.group(0).split('//')[1]
            result[item['siteid']] = grid
        return result

    def get_oa_site_and_grid(self):
        result = {}
        station = StationInfo.objects.all().select_related('company_id', 'grid__grid_name') \
            .values_list('company_id', 'grid__grid_name')
        if station:
            for item in station:
                result[item[0]] = item[1]
        return result

    @list_route(methods=['get'])
    def statistical_grid(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Not_In_Oa_Grid.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"云平台-grid数据统计", today])

        ali_dict = self.get_ali_site_and_grid()
        oa_dict = self.get_oa_site_and_grid()
        # 判断grid是否在oa
        ali_list = list(ali_dict.items())
        oa_list = list(oa_dict.values())
        writer.writerow([f"序号", f"grid", f"siteid"])
        i = 0
        for site, grid in ali_list:
            if grid in oa_list:
                continue
            else:
                writer.writerow([i, grid, site])
                i += 1
        return response

    @list_route(methods=['get'])
    def statistical_site_and_grid(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Not_Match_Grid_And_Site.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"云平台-数据统计", today])
        writer.writerow([f"序号", f"oa_site", f"oa_grid", f"ali_grid"])
        ali_dict = self.get_ali_site_and_grid()
        oa_dict = self.get_oa_site_and_grid()

        ali_site_list = list(ali_dict.items())
        oa_site_list = list(oa_dict.keys())
        i = 0
        for site, grid in ali_site_list:
            if site in oa_site_list:
                # 判断ali数据库与oa数据库数据是否一致
                if grid == oa_dict[site]:
                    continue
                else:
                    min_list = [i, site, oa_dict[site], grid]
                    writer.writerow(min_list)
                    i += 1
            else:
                continue

        return response
