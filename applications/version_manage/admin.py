from django.contrib import admin

# Register your models here.
from .models import VersionProduct, VersionRepository

admin.site.register(VersionRepository)
admin.site.register(VersionProduct)

