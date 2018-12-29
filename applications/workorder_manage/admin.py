from django.contrib import admin

from applications.workorder_manage.models import StationInfo, OpenStationManage, CompanyInfo,CompanyUrl

admin.site.register(StationInfo)
admin.site.register(OpenStationManage)
admin.site.register(CompanyInfo)
admin.site.register(CompanyUrl)
