from django.contrib import admin

from applications.log_manage.models import OperateLog


class OperateLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'operationmodule', 'ip', 'operationtime']
    search_fields = ['user', 'operationmodule', 'ip', 'action']
    readonly_fields = ['user', 'action', 'operationmodule', 'ip', 'operationtime']


admin.site.register(OperateLog, OperateLogAdmin)
