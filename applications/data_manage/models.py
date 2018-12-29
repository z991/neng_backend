import datetime

from django.db import models

from applications.workorder_manage.models import OpenStationManage
from common.models import DataHistoryModel, TimeStampModel
from ldap_server.configs import CHANNEL_CHOICES, OPERATE_ACTION_CHOICES, OPERATE_CREATE, OPERATE_RENEWAL, \
    OPERATE_ADD_PRODUCT, OPERATE_ONLINE, OPERATE_OFFLINE, REFACTORING_CHANNEL_CHOICES, DEPLOY_WAYS
from libs.datetimes import date_to_str


class InquiriesData(DataHistoryModel):
    """
    渠道咨询量数据，远程定时获取
    """
    company_id = models.CharField(max_length=50, help_text="站点ID")
    channel = models.SmallIntegerField(choices=CHANNEL_CHOICES, help_text="渠道类别")
    inquires_num = models.IntegerField(default=0, help_text="咨询量")
    server_grp = models.CharField(max_length=200, help_text="服务组", null=True, blank=True)
    grid = models.CharField(max_length=64, help_text="节点")
    open = models.ForeignKey(OpenStationManage, related_name='inquiries_data', null=True, db_constraint=False)

    class Meta:
        verbose_name_plural = verbose_name = "渠道别咨询量记录"
        permissions = (
            ("view_pandect", "查看总览"),
            ("view_channel-inquiries", "查看线上渠道情况"),
            ("view_customer-use", "查看客户使用情况"),
            ("view_grid-inquiries", "查看节点情况"),
            ("view_sergrp-inquiries", "查看服务组情况"),
        )

    def __str__(self):
        str_date = date_to_str(self.date)
        return f"{self.company_id}-{str_date}"


class OnlineClientData(DataHistoryModel):
    """
    线上站点数据，远程定时获取
    """
    online_num = models.IntegerField(default=0, help_text="在线客户数量")

    class Meta:
        verbose_name_plural = verbose_name = "在线客户数量"
        permissions = (
            ("view_online-client", "查看线上站点情况"),
        )

    def __str__(self):
        return date_to_str(self.date)


class OnlineProductData(DataHistoryModel):
    """
    线上产品数据,远程定时获取
    """
    online_num = models.IntegerField(default=0, help_text="在线客户使用产品数量")
    product_id = models.CharField(max_length=50, help_text="产品ID")

    class Meta:
        verbose_name_plural = verbose_name = "在线产品使用数量"
        permissions = (
            ("view_online-product", "查看线上产品情况"),
        )

    def __str__(self):
        str_date = date_to_str(self.date)
        return f"{self.product_id}-{str_date}"


class OperatingRecord(DataHistoryModel):
    """
    站点运营数据，开站新增、修改、修改上线状态时写入
    """
    action = models.SmallIntegerField(choices=OPERATE_ACTION_CHOICES, help_text="操作行为")
    num = models.IntegerField(default=0, help_text="统计数量")

    class Meta:
        verbose_name_plural = verbose_name = "运营记录"
        permissions = (
            ("view_site-oper", "查看站点运营情况"),
        )

    @classmethod
    def record_create(cls, site_id):
        """新增客户"""
        site = OpenStationManage.objects.filter(station_info__company_id=site_id).first()
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_CREATE,
        )
        record.num += 1
        record.save()

    @classmethod
    def record_renewal(cls, site_id):
        """续费客户"""
        site = OpenStationManage.objects.filter(station_info__company_id=site_id).first()
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_RENEWAL,
        )

        record.num += 1
        record.save()

    @classmethod
    def record_add_product(cls, site_id):
        """新增产品用户"""
        site = OpenStationManage.objects.filter(station_info__company_id=site_id).first()
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_ADD_PRODUCT,
        )
        record.num += 1
        record.save()

    @classmethod
    def record_online(cls, site_id):
        """上线用户"""
        site = OpenStationManage.objects.filter(station_info__company_id=site_id).first()
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_ONLINE,
        )
        record.num += 1
        record.save()

    @classmethod
    def record_offline(cls, site_id):
        """下线用户"""
        site = OpenStationManage.objects.filter(station_info__company_id=site_id).first()
        record, _ = OperatingRecord.objects.get_or_create(
            industry=site.company_info.industry.industry,
            deploy_way=site.station_info.deploy_way,
            cli_version=site.station_info.cli_version,
            date=datetime.date.today(),
            action=OPERATE_OFFLINE,
        )
        record.num += 1
        record.save()


class RefactoringConsultingAndVisitors(TimeStampModel):
    # 日期
    date = models.DateField()
    # 企业id（站点）
    company_id = models.CharField(max_length=50, help_text="站点ID")
    # 有效咨询
    valid_consulting = models.IntegerField(default=0)
    # 无效咨询
    invalid_consulting = models.IntegerField(default=0)
    # 有效访客
    valid_visitors = models.IntegerField(default=0)
    # 无效访客
    invalid_visitors = models.IntegerField(default=0)
    # uv
    unique_vistor = models.IntegerField(default=0)
    # 渠道
    channel = models.SmallIntegerField(choices=REFACTORING_CHANNEL_CHOICES, default=-1, help_text="渠道类别")
    grid = models.CharField(max_length=30, help_text="节点")
    industry = models.CharField(max_length=30, help_text="行业")
    deploy = models.SmallIntegerField(choices=DEPLOY_WAYS, default=1, help_text="部署方式")

    class Meta:
        verbose_name_plural = verbose_name = '咨询量访客量重构版'
        permissions = (("view_re-consulting-and-visitors", "查看咨询访客量"),)


class VistorData(models.Model):
    """
    访客量数据，远程定时获取
    """
    company_id = models.CharField(max_length=50, help_text="站点ID")
    industry = models.CharField(max_length=60, help_text="所属行业")
    deploy_way = models.SmallIntegerField(choices=DEPLOY_WAYS, help_text="部署方式")
    grid = models.CharField(max_length=64, help_text="节点")
    created_at = models.DateTimeField(auto_now=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now_add=True, help_text="更新时间")
    date = models.DateField(help_text="记录时间")
    visitor_num = models.IntegerField(default=0, null=True, blank=True, help_text="访客数量")

    def __str__(self):
        return self.company_id