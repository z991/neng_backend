from django.db import models
from django.db.models import DateTimeField, CASCADE
from django.contrib.auth.models import User
from ldap_server.configs import VERSION_ID, REMARK_TYPE
from applications.setup.models import SiteReceptionGroup
from common.models import SoftDeleteModel, TimeStampModel
from applications.production_manage.models import Grid, Product, SingleSelection, ServerGroup
from ldap_server.configs import STATION_CHOICES, CUSTOM_TYPES, DEPLOY_WAYS, CLI_CHOICES, CUSTOM_NEW, \
    PROD_SERV_VERSIONS, BRAND_EFFECT_CHOICES, CUSTOMER_LEVEL_CHOICES, TRAINING_METHOD_CHOICES, \
    SPECIAL_SELECTION_CHOICES, LINK_TYPE_CHOICES, TRANSMITTING_STATE_CHOICES, \
    MATTER_TYPE, MATTER_STATUS,Y_NLEGACY,TRAINING_METTART_METHOD,SATISFACTION_SURVEY, \
    PRODUCT_STATUS, ATTACHMENT_TYPE, REJECT_TYPE


class CompanyUrl(models.Model):
    """公司网址"""
    company_info = models.ForeignKey('CompanyInfo', related_name='company_url', db_constraint=False, null=True)
    company_url = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.company_url


class AreaInfo(models.Model):
    """地区表"""
    atitle = models.CharField(max_length=50)
    aPArea = models.ForeignKey('AreaInfo', null=True)

    class Meta:
        permissions = (
            ("view_areainfo", "Can see available area info"),
        )


class CompanyAddress(models.Model):
    """公司地址"""
    province = models.ForeignKey('AreaInfo', null=True, related_name='province', db_constraint=False)
    city = models.ForeignKey('AreaInfo', null=True, related_name='city', db_constraint=False)
    detail = models.CharField(max_length=100)

    def __str__(self):
        return "%s-%s-%s" % (self.province.atitle, self.city.atitle, self.detail)


class Industry(SoftDeleteModel, TimeStampModel):
    """所属行业"""
    industry = models.CharField(max_length=60)

    class Meta:
        permissions = (
            ("view_industry", "Can see available industry"),
        )

    def __str__(self):
        return self.industry


class ContactInfo(models.Model):
    """联系信息"""
    station = models.ForeignKey('OpenStationManage', related_name='link_info', db_constraint=False, null=True)
    company = models.ForeignKey('CompanyInfo', related_name='link_info', db_constraint=False, null=True)

    # 联系人 单行文本框 linkman 字符串 - /必填
    linkman = models.CharField(max_length=50, null=True, blank=True)

    # 联系电话 单行文本框 link_phone 字符串 12 / 必填
    link_phone = models.CharField(max_length=30, null=True, blank=True)

    # 电子邮箱 单行文本框 link_email 字符串 50 / 必填
    link_email = models.CharField(max_length=50, null=True, blank=True)

    # QQ号 单行文本框 link_qq 字符串 15 / 必填 
    link_qq = models.CharField(max_length=20, null=True, blank=True)

    # 联系人类别  类型分为：1=客户方业务，2=客户方项目，3=客户方技术，4=商务（小能）
    link_type = models.IntegerField(choices=LINK_TYPE_CHOICES, default=1)

    # 联系人职务（不必填）
    link_work = models.CharField(max_length=20, null=True, blank=True)


class AccountConf(models.Model):
    """账户配置"""
    station = models.ForeignKey('OpenStationManage', related_name='account_conf', db_constraint=False, null=True)
    # 用户名  单行文本框  user_name  字符串  必填
    user_name = models.CharField(max_length=50)

    # 设置密码  单行文本框  set_pwd  字符串  16 / 必填
    set_pwd = models.CharField(max_length=200, null=True, blank=True)


class CompanyInfo(models.Model):
    # 站点类型 下拉列表框  整型：站点类型  试用客户1  正式客户2  市场渠道客户3  商务渠道客户4  自用站点5 / 必填
    station_type = models.IntegerField(choices=STATION_CHOICES, blank=True, null=True)

    # 公司名称 单行文本框 company_name 字符串 50 / 必填
    company_name = models.CharField(max_length=50)

    # 【外键】公司网址 单行文本框 company_url 数组

    # 公司地址 下拉列表框 单行文本框 company_address 对象 256 / 必填
    company_address = models.OneToOneField(CompanyAddress, related_name='company_info',
                                           on_delete=models.CASCADE, null=True)
    # 公司简称 单行文本框 abbreviation
    abbreviation = models.CharField(max_length=50)

    # 公司邮箱 单行文本框 company_email 字符串 50 / 必填
    company_email = models.CharField(max_length=50)

    # 【外键】 所属行业 下拉列表框 industry 字符串 必填
    industry = models.ForeignKey(Industry, related_name='company_info', db_constraint=False, null=True)

    # 营业执照名称 单行文本框 GSZZ 字符串 50 / 必填
    GSZZ = models.CharField(max_length=50)

    # 客户性质  customer_type  布尔  新客户:0, 老客户信息补录:1  / 必填
    customer_type = models.BooleanField(choices=CUSTOM_TYPES, default=CUSTOM_NEW)

    # 客服工作区域 单行文本框 service_area 字符串 128 / 必填
    service_area = models.CharField(max_length=128)

    # 业务模式 下拉列表框 cli_version  客户版本选项：b2b2c b2c
    cli_version = models.IntegerField(choices=CLI_CHOICES, blank=True, null=True)

    # 部署方式 下拉列表框 deploy_way 整数：1.标准版 2.vip;3.vpc;4.企业版 /必填 部署方式选项：标准版 vip vpc 企业版
    deploy_way = models.IntegerField(choices=DEPLOY_WAYS, blank=True, null=True)

    # 产品分类 经典版 重构版
    classify = models.SmallIntegerField(choices=PROD_SERV_VERSIONS, blank=True, null=True)

    # 品牌效应  下拉   世界500强、中国500强、行业前10   默认为‘无’或者‘否’
    brand_effect = models.IntegerField(choices=BRAND_EFFECT_CHOICES, default=0)

    # 客户级别  下拉 A,B,C  默认为‘无’或者‘否’
    customer_level = models.IntegerField(choices=CUSTOMER_LEVEL_CHOICES, default=0)

    # 平台信息  文本框  如网址/微信公众号/wap站等信息
    platform_informatiom = models.TextField(verbose_name="平台信息", null=True, blank=True)

    # 培训方式  下拉  分为：远程、现场、远程+现场。  默认为‘无’或者‘否’
    training_method = models.IntegerField(choices=TRAINING_METHOD_CHOICES, default=0)

    # UV / 天   文本框
    visitor = models.IntegerField(default=0)

    # PV / 天   文本框
    consult = models.IntegerField(default=0)

    # 是否已特批  下拉  如选择未签署，【是否已特批】字段需选择“是”，老客户请填“否”  默认为‘无’或者‘否’
    special_selection = models.IntegerField(choices=SPECIAL_SELECTION_CHOICES, default=0)

    # 是否签署合同   下拉 Y / N  默认为‘无’或者‘否’
    sign_contract = models.IntegerField(choices=SPECIAL_SELECTION_CHOICES, default=0)

    # 坐席数  文本框
    kf_number = models.IntegerField(default=0)

    # 订单信息
    order_info = models.ForeignKey("OrderManage", null=True, blank=True, related_name='company_info')

    # 驳回理由   记录每一条驳回理由 在修改里面一直新增
    comment = models.TextField(null=True, blank=True, verbose_name='驳回理由')

    # 流转状态
    transmitting_state = models.IntegerField(choices=TRANSMITTING_STATE_CHOICES, default=1)

    class Meta:
        verbose_name = verbose_name_plural = "公司信息"

    def __str__(self):
        return self.company_name


class OrderManage(models.Model):
    # 合同开始时间
    contract_start_time = models.DateField(verbose_name='合同开始时间', default='')
    # 合同结束时间
    contract_end_time = models.DateField(verbose_name='合同结束时间', default='')
    # 合同编号
    contract_index = models.CharField(max_length=30, verbose_name='合同编号', null=True, blank=True)
    # 附件
    contract_accessory = models.TextField(verbose_name="附件", null=True, blank=True)
    # 合同金额
    contract_amount = models.CharField(null=True, max_length=12, blank=True, default='', verbose_name='合同金额')
    # 回款金额
    amount_cashed = models.CharField(null=True, max_length=12, blank=True, default='', verbose_name='回款金额')
    # 回款时间
    cashed_time = DateTimeField(verbose_name='回款时间', auto_now=True)
    # 创建时间
    created_at = DateTimeField(auto_now=True, verbose_name="创建时间")
    # 合同内容 功能模块
    contract_content = models.TextField(max_length=150, verbose_name='合同内容', null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "订单信息"


class StationInfo(models.Model):
    # 企业ID 单行文本框 company_id 字符串 20 / 必填
    company_id = models.CharField(max_length=20, unique=True)
    # 部署方式 下拉列表框 deploy_way 整数：1.标准版 2.vip;3.vpc;4.企业版 /必填 部署方式选项：标准版 vip vpc 企业版
    deploy_way = models.IntegerField(choices=DEPLOY_WAYS, null=True)

    # 有效期 / 天 单行文本框 validity_days 整数 4 / 必填 输入限制：数字
    validity_days = models.IntegerField()

    # 节点选择 下拉列表框 grid 对象 必填 数据来源已创建的节点；选择部署方式后才可选择节点
    # apps.get_app_config('production_manage').get_model('Grid')
    grid = models.ForeignKey(Grid, null=True,
                             related_name='station_info', db_constraint=False)

    server_grp = models.ForeignKey(ServerGroup, null=True)

    # 业务模式 下拉列表框 cli_version  必填 客户版本选项：b2b2c b2c
    cli_version = models.IntegerField(choices=CLI_CHOICES, blank=True, null=True)

    # 产品分类 经典版 重构版
    classify = models.SmallIntegerField(choices=PROD_SERV_VERSIONS, null=True, help_text="产品类别")

    # 合同产品 复选按钮 pact_products 列表 必填 数据来源于已创建的产品
    pact_products = models.ManyToManyField(Product, related_name='station_info', db_constraint=False)

    # 开站日期 日历控件 open_station_time 字符串 必填 不可选择历史日期
    open_station_time = models.DateField()

    # 到期日期 文字信息 close_station_time 字符串 必填 数据来源于已录入的从开站日期开始计算有效期，得出的结束时间；
    close_station_time = models.DateField()

    # 销售人员 单行文本框 sales 字符串 - / 必填
    sales = models.CharField(max_length=254, null=True, default="")
    # 售前人员 单行文本框 pre_sales 字符串 - / 必填
    pre_sales = models.CharField(max_length=254, null=True, default="")
    # 运营顾问 单行文本框 oper_cslt 字符串 - / 必填
    oper_cslt = models.CharField(max_length=254, null=True, default="")
    # 实施顾问 单行文本框 impl_cslt 字符串 - / 必填
    impl_cslt = models.CharField(max_length=254, null=True, default="")
    # 运营支持 单行文本框 oper_supt 字符串 - / 必填
    oper_supt = models.CharField(max_length=254, null=True, default="")
    # 开站标识
    order_work = models.CharField(default="页面创建", max_length=18, verbose_name='开站标识')
    # 帮助中心
    set_up = models.ForeignKey(SiteReceptionGroup, default='', null=True, blank=True, related_name='set_info')
    # 版本id
    version_id = models.SmallIntegerField(choices=VERSION_ID, default=1, verbose_name='版本ID')

    class Meta:
        verbose_name = verbose_name_plural = "站点信息"

    def __str__(self):
        return self.company_id

    @property
    def classsify_name(self):
        return dict(PROD_SERV_VERSIONS)[self.classify]


class OpenStationManage(SoftDeleteModel, TimeStampModel):
    STATUS_OFFLINE = False
    STATUS_ONLINE = True
    STATUS_TYPES = (
        (STATUS_OFFLINE, "下线"),
        (STATUS_ONLINE, "上线"),
    )
    online_status = models.BooleanField(default=False, choices=STATUS_TYPES)

    # 企业信息
    company_info = models.OneToOneField(CompanyInfo, related_name='open_station',
                                        on_delete=models.CASCADE, null=True)
    # 联系人信息
    # 【外键】 联系人信息：点击增加联系人 联系电话 电子邮箱和QQ号文本；最多增加三个联系人；增加的文本均必填。

    # 站点信息
    station_info = models.OneToOneField(StationInfo, related_name='open_station',
                                        on_delete=models.CASCADE, null=True)
    # 功能开关列表信息
    # func_list 选项 单行文本框、下拉列表框 selections 对象 选填 数据来源于功能开关带动的文本类型
    func_list = models.ManyToManyField(SingleSelection, related_name='station', db_constraint=False)

    its_parent = models.ForeignKey('self', max_length=18, related_name="parent", null=True, default="", verbose_name="子站的父类id")

    # 联系人信息
    # 【外键】 联系人信息：点击增加联系人 联系电话 电子邮箱和QQ号文本；最多增加三个联系人；增加的文本均必填。

    # 【外键】 账户配置信息
    class Meta:
        permissions = (
            ("view_openstationmanage", "Can see available open station manage"),

        )
        verbose_name = verbose_name_plural = "开站管理"

    def __str__(self):
        return self.station_info.company_id


class RemarkEvolve(models.Model):
    operationtime = models.DateTimeField(auto_now=True, verbose_name="创建时间")
    user = models.ForeignKey(User, on_delete=CASCADE, null=True, verbose_name="用户")
    content = models.TextField(verbose_name="内容")
                #  1:备注  3:沟通结果
    mark_type = models.IntegerField(choices=REMARK_TYPE, blank=True, null=True, verbose_name="备注类型")
    correlation_id = models.CharField(max_length=8, verbose_name="关联id")

    class Meta:
        verbose_name_plural = verbose_name = "客户库备注"

    def __str__(self):
        return self.id


class Matter(TimeStampModel):
    """
    培训问题相关字段
    """
    matter_type = models.SmallIntegerField(choices=MATTER_TYPE, blank=True, null=True, verbose_name="问题类型")
    matter_status = models.SmallIntegerField(choices=MATTER_STATUS, blank=True, null=True, verbose_name="问题状态")
    training_method = models.SmallIntegerField(choices=TRAINING_METTART_METHOD, blank=True, null=True, verbose_name="培训方式")
    legacy_issue = models.SmallIntegerField(choices=Y_NLEGACY, blank=True, null=True, verbose_name="是否有遗留问题")
    satisfaction_level = models.SmallIntegerField(choices=SATISFACTION_SURVEY, blank=True, null=True, verbose_name="满意度等级")

    final_training_method = models.SmallIntegerField(choices=TRAINING_METTART_METHOD, blank=True, null=True,
                                                     verbose_name="最终培训方式")
    matter_name = models.CharField(max_length=64, verbose_name="问题名称", null=True)
    training_contact = models.CharField(max_length=16, verbose_name="培训联系人职位", null=True)
    training_contactnum = models.CharField(max_length=16, verbose_name="培训联系人电话", null=True)
    training_contactqq = models.CharField(max_length=16, verbose_name="培训人QQ", null=True)
    training_position = models.CharField(max_length=16, verbose_name="培训联系人职位", null=True)

    invest_start = models.DateTimeField(verbose_name="调查开始时间", null=True)
    invest_end = models.DateTimeField(verbose_name="调查结束时间", null=True)
    start_time = models.DateTimeField(null=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, verbose_name="结束时间")

    description_customer = models.TextField(null=True, verbose_name="客户现状描述")
    online_module = models.TextField(verbose_name="已上线模块", null=True)
    unonline_module = models.TextField(verbose_name="未上线模块", null=True)
    communication_way = models.TextField(null=True, verbose_name="沟通方式")
    untrained_cause = models.TextField(null=True, verbose_name="未培训原因")
    termination_reason = models.TextField(null=True, verbose_name="终止原因")
    customer_training_needs = models.TextField(verbose_name="客户培训需求", null=True)
    training_model = models.TextField(verbose_name="培训模块", null=True)
    problem_description = models.TextField(verbose_name="问题描述", null=True)
    customer_feedback = models.TextField(verbose_name="客户反馈详情", null=True)
    # 和公司外键
    company_matter = models.CharField(max_length=16, verbose_name="企业id", null=True)
    # 人
    responsible = models.ForeignKey(User, related_name="response_user", db_constraint=False, null=True, verbose_name="经办人")
    training_instructors = models.ForeignKey(User, verbose_name="培训讲师", related_name="instructors",  null=True, db_constraint=False)
    dealing_person = models.ForeignKey(User, verbose_name="处理人",related_name="dealing", null=True, db_constraint=False)
    investigador = models.ForeignKey(User, verbose_name="调查人员", related_name="investigate", null=True, db_constraint=False)

    class Meta:
        verbose_name_plural = verbose_name = "培训相关问题"

    def __str__(self):
        return self.matter_name


class Reject(TimeStampModel):
    """
    驳回理由
    """
    dismiss_reason = models.TextField(verbose_name="驳回理由", null=True)
    correlation_id = models.CharField(max_length=8, verbose_name="关联id")
    reject_type = models.SmallIntegerField(choices=REJECT_TYPE, blank=True, null=True, verbose_name="驳回理由类型")

    class Meta:
        verbose_name_plural = verbose_name = "培训问题驳回理由"

    def __str__(self):
        return self.id


class Attachment(TimeStampModel):
    """
    附件表
    """
    enclosure = models.TextField(verbose_name="附件", null=True)
    step_atta = models.CharField(max_length=64, verbose_name="操作步骤", null=True)
    atta_type = models.SmallIntegerField(choices=ATTACHMENT_TYPE, blank=True, null=True, verbose_name="附件类型")
    correlation_id = models.CharField(max_length=8, verbose_name="关联id")

    class Meta:
        verbose_name_plural = verbose_name = "培训问题上传的附件"

    def __str__(self):
        return self.id


class ProductConfig(TimeStampModel):
    # 子站点
    children_station = models.CharField(max_length=20, null=True, verbose_name="子站点")
    # 开站id
    open_id = models.CharField(max_length=16, verbose_name="开站id")
    # 工单主题
    workorder_theme = models.CharField(max_length=50, null=True, verbose_name="工单主题")
    # 所属模块
    subordinatemodule = models.CharField(max_length=128, null=True, verbose_name="所属模块")
    # 功能名称
    func_name = models.CharField(max_length=128, null=True, verbose_name="功能名称")
    # 功能选项值
    func_value = models.TextField(null=True, verbose_name="功能选项值")
    # 描述
    describe = models.CharField(max_length=200,null=True, verbose_name="描述")
    # 分配人
    allocation_people = models.CharField(max_length=16, verbose_name="分配人", null=True)
    # 处理人
    dealing_person = models.ForeignKey(User, verbose_name="处理人", related_name="product_dealing", null=True, db_constraint=False)
    # 产品配置状态
    product_stautus = models.SmallIntegerField(choices=PRODUCT_STATUS, blank=True, null=True, verbose_name="产品配置状态")
    # KHKid
    khk_id = models.CharField(max_length=8, verbose_name="客户库id")
    # 分配时间
    allocate_time = models.DateTimeField(null=True, verbose_name="分配时间")
    # 实际开始时间
    actual_start_time = models.DateTimeField(null=True, verbose_name="实际开始时间")
    # 实际完成时间
    actual_completion_time = models.DateTimeField(null=True, verbose_name="实际完成时间")

    class Meta:
        verbose_name_plural = verbose_name = "产品配置"

    def __str__(self):
        return self.workorder_theme