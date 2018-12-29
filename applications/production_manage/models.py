from django.db import models

# Create your models here.
from common.models import SoftDeleteModel, TimeStampModel
from ldap_server.configs import CLI_CHOICES, PROD_SERV_VERSIONS, CLOUD_CLASS


class Product(SoftDeleteModel, TimeStampModel):
    """
    产品名称
    """
    product = models.CharField(max_length=100, null=False, unique=True)  # 产品名称
    classify = models.SmallIntegerField(choices=PROD_SERV_VERSIONS, null=False, help_text="产品类别")

    class Meta:
        permissions = (
            ("view_product", "Can see available products"),
        )
        verbose_name_plural = verbose_name = "产品名称"

    def __str__(self):
        return self.product


class VersionInfo(SoftDeleteModel, TimeStampModel):
    """
    各版本信息
    """
    product = models.ForeignKey('Product', related_name='version', db_constraint=False, null=True)  # 产品
    pro_version = models.CharField(max_length=30, null=False)  # 产品版本
    function = models.ManyToManyField('FunctionInfo', related_name='version', db_constraint=False)  # 功能开关

    class Meta:
        permissions = (
            ("view_versioninfo", "Can see available versioninfos"),
        )
        verbose_name_plural = verbose_name = "版本信息"

    def __str__(self):
        return '%s: %s' % (self.product, self.pro_version)


class FunctionInfo(SoftDeleteModel):
    """
    经典版功能开关
    """
    # 版本信息
    product = models.ForeignKey('Product', null=True, related_name='function', db_constraint=False)
    # 功能名称
    func_name = models.CharField(max_length=100, null=False)
    # 客户版本  --展示条件
    cli_version = models.IntegerField(choices=CLI_CHOICES)  # 1.B2B 2.B2C 3.不限
    # 功能路径（所属字段）
    func_code = models.CharField(max_length=100, null=False)

    # 文本类型
    func_type = models.CharField(max_length=30, null=False)  # ：文本框 ：单选

    # 父级展示条件
    parent = models.ManyToManyField('SingleSelection', related_name='childfunc', db_constraint=False)

    # 关联展示条件
    dependences = models.ManyToManyField('SingleSelection', related_name='relatedfunc', db_constraint=False)

    class Meta:
        verbose_name_plural = verbose_name = "功能信息"

    def __str__(self):
        return self.func_name


class SingleSelection(SoftDeleteModel):
    """
    经典版功能开关中的单选项
    """
    # 功能信息
    function = models.ForeignKey('FunctionInfo', related_name='selection', db_constraint=False, null=True)
    # 选项名称
    select_name = models.CharField(max_length=100, null=False)
    # 选项值
    select_value = models.CharField(max_length=100, null=False)
    # 是否默认
    is_default = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("view_singleselection", "Can see available single selection"),
        )
        verbose_name_plural = verbose_name = "功能开关"

    def __str__(self):
        return "%s: %s" % (self.function, self.select_name)


class SerType(models.Model):
    """
    服务类型
    """

    ser_type = models.CharField(max_length=50, unique=True)  # 服务类型
    version_type = models.SmallIntegerField(choices=PROD_SERV_VERSIONS)
    cor_product = models.ManyToManyField('Product', related_name='sertype', db_constraint=False)  # 关联产品

    class Meta:
        permissions = (
            ("view_sertype", "Can see available ser type"),
        )
        verbose_name_plural = verbose_name = "服务类型"

    def __str__(self):
        return self.ser_type


class Server(SoftDeleteModel, TimeStampModel):
    """
    运维配置的服务id项，用于客服管理中为客户开站提供服务id配置
    """
    ser_id = models.CharField(max_length=100)  # 服务id
    version_type = models.SmallIntegerField(choices=PROD_SERV_VERSIONS)   # 类型 1.金典版; 2.重构版;
    ser_name = models.ForeignKey('SerType', null=True, related_name='server', db_constraint=False)  # 服务

    class Meta:
        permissions = (
            ("view_server", "Can see available servers"),
        )
        verbose_name_plural = verbose_name = "服务器"

    def __str__(self):
        return "%s" % (self.ser_name,)


class SerAddress(models.Model):
    server = models.ForeignKey('Server', null=True, related_name='ser_url', db_constraint=False)  # 服务id
    ser_address = models.CharField(max_length=200)  # 服务地址

    class Meta:
        permissions = (
            ("view_seraddress", "Can see available ser address"),
        )
        verbose_name_plural = verbose_name = "服务地址"

    def __str__(self):
        return self.ser_address


class SerIp(models.Model):
    ser_address = models.ForeignKey('SerAddress', null=True, related_name='ser_ip', db_constraint=False)  # 服务地址
    ser_ip = models.CharField(max_length=50)  # 服务ip

    def __str__(self):
        return self.ser_ip

    class Meta:
        verbose_name_plural = verbose_name = "服务器IP"


class DataBaseInfo(models.Model):
    """
    数据库配置
    """
    # 数据库类型
    db_type = models.CharField(max_length=100)
    # 数据库地址
    db_address = models.CharField(max_length=500)
    # 数据库名称
    db_name = models.CharField(max_length=100)
    # 用户名
    db_username = models.CharField(max_length=100)
    # 密码
    db_pwd = models.CharField(max_length=100, help_text="加密后的密码")
    # 端口
    db_port = models.CharField(max_length=100)
    # 对应节点
    grid = models.ForeignKey('Grid', related_name='db_info')  # 数据库配置

    class Meta:
        permissions = (
            ("view_databaseinfo", "Can see available data base info"),
        )
        verbose_name_plural = verbose_name = "数据库信息"

    def __str__(self):
        return "%s: %s" % (self.db_name, self.db_address)


class Grid(TimeStampModel):
    """
    节点信息
    """
    grid_name = models.CharField(max_length=100, unique=True)  # 节点名
    grid_site = models.CharField(max_length=50)  # 机房
    version_type = models.SmallIntegerField(choices=PROD_SERV_VERSIONS)  # 类型 1.金典版; 2.重构版;
    deploy_way = models.IntegerField()  # 部署方式 1.vip; 2.vpc;
    versionInfos = models.ManyToManyField('VersionInfo', related_name='grid', db_constraint=False, default="")  # 版本号
    domain_name = models.CharField(max_length=512, null=True, blank=True,
                                   default="", verbose_name="域名")
    getFlashserver = models.TextField(verbose_name="服务端", default="")
    visitors = models.TextField(verbose_name="访客端", default="")

    class Meta:
        permissions = (
            ("view_grid", "Can see available grids"),
        )
        verbose_name_plural = verbose_name = "节点信息"

    def __str__(self):
        return self.grid_name


class ServerGroup(SoftDeleteModel, TimeStampModel):
    """
    服务组信息
    """
    group_name = models.CharField(max_length=100)  # 服务组名
    version_type = models.SmallIntegerField(choices=PROD_SERV_VERSIONS)  # 类型 1.金典版; 2.重构版;
    grid = models.ForeignKey('Grid', null=True, related_name='group', db_constraint=False)  # 节点
    ser_address = models.ManyToManyField('SerAddress', related_name='group', db_constraint=False)  # 服务地址信息

    class Meta:
        permissions = (
            ("view_servergroup", "Can see available servergroups"),
        )
        verbose_name_plural = verbose_name = "服务组信息"

    def __str__(self):
        return self.group_name


class KsyAliCloud(TimeStampModel):

    grid_name = models.CharField(max_length=100, verbose_name="服务器实例名称")  #服务器实例名称
    date = models.DateField(verbose_name="记录时间")
    cloud = models.SmallIntegerField(choices=CLOUD_CLASS, null=False, verbose_name="云分类") #0：金山云, 1:阿里云
    sum = models.CharField(max_length=100, verbose_name="时间段流量总和")
    allocation_id = models.CharField(max_length=100, verbose_name="eip实例id")

    class Meta:
        verbose_name_plural = verbose_name = "服务器流量统计表"

    def __str__(self):
        return self.grid_name
