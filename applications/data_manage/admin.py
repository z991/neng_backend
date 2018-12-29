# Register your models here.
from django.contrib import admin

from applications.data_manage.models import OnlineProductData, OnlineClientData, InquiriesData


class InquiriesDataAdmin(admin.ModelAdmin):
    list_display = ['company_id', 'channel', 'inquires_num', 'industry', 'deploy_way', 'cli_version', 'created_at',
                    'updated_at', 'date']


class OnlineClientDataAdmin(admin.ModelAdmin):
    list_display = ['online_num', 'industry', 'deploy_way', 'cli_version', 'created_at', 'updated_at', 'date']


class OnlineProductDataAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'industry', 'deploy_way', 'cli_version', 'created_at', 'updated_at', 'date']


admin.site.register(InquiriesData, InquiriesDataAdmin)
admin.site.register(OnlineClientData, OnlineClientDataAdmin)
admin.site.register(OnlineProductData, OnlineProductDataAdmin)
