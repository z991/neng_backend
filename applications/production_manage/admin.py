from django.contrib import admin

# Register your models here.
from applications.production_manage.models import Product, VersionInfo, Server, Grid, ServerGroup, FunctionInfo, \
    SingleSelection, SerAddress, SerType, DataBaseInfo, SerIp

admin.site.register(Product)
admin.site.register(VersionInfo)
admin.site.register(Server)
admin.site.register(Grid)
admin.site.register(ServerGroup)
admin.site.register(FunctionInfo)
admin.site.register(SingleSelection)
admin.site.register(SerType)
admin.site.register(SerAddress)
admin.site.register(SerIp)
admin.site.register(DataBaseInfo)
