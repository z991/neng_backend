from django.contrib import admin

from .models import LdapRole, LdapUser, LdapStructure



class LdapGroupAdmin(admin.ModelAdmin):
    exclude = ['dn']
    list_display = ['cn']
    search_fields = ['cn']


class LdapUserAdmin(admin.ModelAdmin):
    exclude = ['dn']
    list_display = ['username', 'user_sn']
    search_fields = ['username']


class LdapStructureAdmin(admin.ModelAdmin):
    exclude = ['dn']
    list_display = ['ou']
    search_fields = ['ou']


admin.site.register(LdapRole, LdapGroupAdmin)
admin.site.register(LdapUser, LdapUserAdmin)
admin.site.register(LdapStructure, LdapStructureAdmin)
