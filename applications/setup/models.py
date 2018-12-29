from django.db import models
from ldap_server.configs import LOGIN_MODEL, CREATE_SOURCE
from common.models import SoftDeleteModel, TimeStampModel
from django.contrib.auth.models import User, Group


class SiteReceptionGroup(SoftDeleteModel):
    title = models.CharField(max_length=20, help_text="接待组名称")
    group_id = models.CharField(max_length=100, help_text="接待组ID")
    manager = models.CharField(max_length=20, help_text="接待经理", null=True, blank=True)
    phone_number = models.CharField(max_length=20, help_text="电话", null=True, blank=True)
    email = models.EmailField(help_text="Email", null=True, blank=True)
    desc = models.CharField(max_length=100, help_text="一句话介绍", null=True, blank=True)
    url = models.URLField(help_text="网址", null=True, blank=True)
    avatar = models.URLField(help_text="显示头像", default="", null=True, blank=True)

    class Meta:
        permissions = (
            ("view_sitereceptiongroup", "Can see available site_reception_group"),
        )

    @property
    def company_id(self):
        return self.site.company_id


class LoginLdapConfig(models.Model):
    auth_ldap_bind_dn = models.CharField(max_length=64)
    auth_ldap_bind_password = models.CharField(max_length=32)
    user_ldapsearch = models.CharField(max_length=64)
    user_scope_subtree = models.CharField(max_length=24)
    group_ldapsearch = models.CharField(max_length=64)
    group_scope_subtree = models.CharField(max_length=128)
    is_active = models.CharField(max_length=128)
    is_staff = models.CharField(max_length=128)
    is_superuser = models.CharField(max_length=128)
    ldap_server_url = models.CharField(max_length=64)
    login_model = models.SmallIntegerField(choices=LOGIN_MODEL, default=2)
    ldap_name = models.CharField(max_length=128)
    ldap = models.CharField(max_length=8, default="ldap")

    class Meta:
        permissions = (
            ("view_loginconfig", "Can see available loginconfig"),
        )
        verbose_name_plural = verbose_name = "登录模式配置"

    def __str__(self):
        return self.login_model


class UserProfile(models.Model):
    enable_choice = [(0, '软删'), (1, '正常')]
    create_source = models.SmallIntegerField(choices=CREATE_SOURCE, verbose_name='创建来源', default=1)
    is_enable = models.SmallIntegerField(choices=enable_choice, verbose_name='是否软删除', default=1)
    user = models.OneToOneField(User, related_name="user_profile")
