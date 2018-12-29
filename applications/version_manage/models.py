from django.db import models
from datetime import date
import datetime

# Create your models here.
from ldap_server.configs import PROD_SERV_VERSIONS, RELEASE_STATUS_TYPES
from common.models import TimeStampModel
from libs.datetimes import date_to_str


today = date.today()


class VersionRepository(TimeStampModel):
    """版本库表"""
    # 版本号
    version_id = models.CharField(max_length=50)
    # 是否发版
    release_status = models.BooleanField(default=False, choices=RELEASE_STATUS_TYPES)
    # 发版次数
    release_number = models.CharField(max_length=5, default='')
    # 关联父版本id
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, db_constraint=False,
                               verbose_name='父版本')

    class Meta:
        permissions = (
            ("view_versionrepository", "Can see available versionrepository"),
        )
        verbose_name = verbose_name_plural = "版本库表"


class VersionProduct(TimeStampModel):
    """版本产品"""

    version_id = models.ForeignKey(VersionRepository, related_name='version_product', null=True, help_text='版本号')
    # 发版时间
    release_date = models.DateField()
    # 产品名称
    product_name = models.CharField(max_length=50)
    # 产品版本
    product_version = models.CharField(max_length=50, default='')
    # 版本说明
    product_explain = models.TextField()
    # 产品分类
    product_classify = models.SmallIntegerField(choices=PROD_SERV_VERSIONS, null=False, help_text="产品类别")
    # 是否发版
    release_status = models.BooleanField(default=False, choices=RELEASE_STATUS_TYPES)
    # 发版次数
    release_number = models.CharField(max_length=5, default='')

    product_time = date_to_str(datetime.datetime.now(), format='%Y-%m-%d %H:%M:%S')
    # 版本进度
    schedule = models.TextField(default='[{"name": "项目立项","time": "%s","mileage": "1","index": 1},{"name": "产品设计","time": "","mileage": "0","index": 2},{"name": "研发","time": "","mileage": "","index": 3},{"name": "测试","time": "","mileage": "","index": 4},{"name": "产品验收","time": "","mileage": "","index": 5},{"name": "部署","time": "","mileage": "","index": 6},{"name": "发版","time": "","mileage": "","index": 7},{"button_log": {"old": "无","new": "无"},"index": 8}]' % product_time)

    class Meta:
        permissions = (
            ("view_versionproduct", "Can see available versionproduct"),
        )
        verbose_name = verbose_name_plural = "版本产品"


