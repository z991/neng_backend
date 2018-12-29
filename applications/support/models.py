from django.db import models
from ldap_server.configs import PROD_SERV_VERSIONS
# Create your models here.


class ClientDownload(models.Model):
    version_num = models.CharField(max_length=24, null=True, verbose_name="版本号")
    down_address = models.TextField(null=True, verbose_name="下载地址")

    classify = models.SmallIntegerField(choices=PROD_SERV_VERSIONS, blank=True, null=True, verbose_name="版本类型")
    time = models.DateTimeField(auto_now=True, verbose_name="新增时间")

    class Meta:
        verbose_name_plural = verbose_name = "客户端下载模块"

    def __str__(self):
        return self.down_address