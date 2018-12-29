# xbot机器人域名
ROBOT_XBOT_URL = 'http://bj-v100.ntalker.com/'
ROBOT_YUNWEN_URL = 'http://hz-xnfaq.ntalker.com/'

# pv uv 脚本请求接口
GET_USER_URL = f"http://usercenter-svc"
GET_PERMIT_URL = f"http://kpi.ntalker.com/api/report/rpt_oa_service/v1"
GET_DATA_URL = f"http://kpi.ntalker.com/api/report/"

MONTH_KEY = {
    "01": '!@*',
    "02": '%_@',
    "03": '#*@',
    "04": '%$！',
    "05": '%#*',
    "06": '*^+',
    "07": '&#%',
    "08": '*$#',
    "09": '@^*',
    "10": '!*$',
    "11": '_#@',
    "12": '%!&'
}

# 品牌效应
BRAND_EFFECT_DEFAULT = 0
WORLD = 1
CHINA = 2
INDUSTRY = 3
BRAND_EFFECT_CHOICES = (
    (WORLD, "世界500强"),
    (CHINA, "中国500强"),
    (INDUSTRY, "行业前10"),
    (BRAND_EFFECT_DEFAULT, "无"),
)

# 客户级别
CUSTOMER_LEVEL_CHOICES = (
    (0, '无'),
    (1, 'A'),
    (2, 'B'),
    (3, 'C'),
)

# 培训方式
TRAINING_METHOD_CHOICES = (
    (0, '无'),
    (1, '远程'),
    (2, '现场'),
    (3, '远程+现场'),
)

# 是否已特批
SPECIAL_SELECTION_CHOICES = (
    (0, '否'),
    (1, '是'),
)

# 联系人类别
LINK_TYPE_CHOICES = (
    (1, '客户方业务'),
    (2, '客户方项目'),
    (3, '客户方技术'),
    (4, '商务（小能）'),
)

# 流转状态
TRANSMITTING_STATE_CHOICES = (
    (0, '审批通过'),
    (1, '待审批'),
    (2, '审批驳回'),
    (3, '上线')
)

# 部署方式
DEPLOY_STANDARD = 1
DEPLOY_VIP = 2
DEPLOY_VPC = 3
DEPLOY_OEM = 4
DEPLOY_QS = 5
DEPLOY_WAYS = (
    (DEPLOY_STANDARD, "标准版"),
    (DEPLOY_VIP, "公有云"),
    (DEPLOY_VPC, "专属云"),
    (DEPLOY_OEM, "私有云"),
    (DEPLOY_QS, "缺省"),
)

# 客户版本
CLI_B2B = 1
CLI_B2C = 2
CLI_B2B2C = 4
CLI_UNLIMITED = 3
CLI_CHOICES = (
    (CLI_B2B, "B2B"),
    (CLI_B2C, "B2C"),
    (CLI_UNLIMITED, "不限"),
    (CLI_B2B2C, "B2B2C"),
)

# 功能模块
FUNCTION_SELECT = (
    (1, 'Web'),
    (2, 'WAP'),
    (3, 'ERP'),
    (4, 'SDK-Android'),
    (5, 'SDK-IOS'),
    (6, '微信'),
    (7, '云问机器人(SAAS版)'),
    (8, '云问机器人(本地部署版)'),
    (9, 'XBot机器人(SAAS版)'),
    (10, 'XBot机器人(本地部署版)'),
    (11, '呼叫中心'),
    (12, '工单'),
    (13, 'HTTPS服务'),
    (14, '二维码'),
    (15, '微博'),
    (16, '小能手机客户端'),
    (17, '微信小程序'),
    (18, '企业微信'),
    (19, '企业QQ'),
    (20, '个人QQ'),
    (21, 'API-获取客户账户信息接口'),
    (22, 'API-获取客户账户分组接口'),
    (23, 'API-获取商户分类接口'),
    (24, 'API-获取商户信息接口'),
    (25, 'API-创建商户接口'),
    (26, 'API-获取接待组接口'),
    (27, 'API-创建接待组接口'),
    (28, 'API-支付订单同步接口'),
    (29, 'API-获取在线咨询记录接口'),
    (30, 'API-获取在线咨询详细消息接口'),
    (31, 'API-获取留言记录接口'),
    (32, 'API-获取咨询KPI数据接口'),
    (33, 'API-获取访客轨迹接口'),
    (34, 'API-获取用户资源数据接口'),
    (35, 'API-创建通知'),
    (36, 'API-获取呼叫中心基本信息'),
    (37, 'API-获取接待组客服在线状态接口'),
    (38, 'API-获取离线消息接口'),
    (39, '增强应用-会话协助&接管'),
    (40, '增强应用-实时监控'),
    (41, '增强应用-搜索引擎关键词'),
    (42, '定制服务-前端UI定制'),
    (43, '定制服务-现场实施'),
    (44, '定制服务-现场培训'),
    (45, '定制服务-ERP信息定制'),

)

# 站点类型
STATION_TRIAL = 1
STATION_OFFICAL = 2
STATION_MARKET = 3
STATION_BUSINESS = 4
STATION_PERSONAL = 5
STATION_CHOICES = (
    (STATION_TRIAL, "试用客户"),
    (STATION_OFFICAL, "正式客户"),
    (STATION_MARKET, "市场渠道客户"),
    (STATION_BUSINESS, "商务渠道客户"),
    (STATION_PERSONAL, "自用站点"),
)

# 客户类型
CUSTOM_NEW = False
CUSTOM_OLD = True
CUSTOM_TYPES = (
    (CUSTOM_NEW, "新客户"),
    (CUSTOM_OLD, "老客户"),
)

# 咨询渠道
CHANNEL_UNKNOWN = -1
CHANNEL_PC = 6
CHANNEL_WECHAT = 1
CHANNEL_APP = 2
CHANNEL_WAP = 3
CHANNEL_IOS = 4
CHANNEL_ANDROID = 5
CHANNEL_WEIBO = 7
CHANNEL_QQ = 8

CHANNEL_CHOICES = (
    (CHANNEL_PC, "PC"),
    (CHANNEL_WECHAT, "微信"),
    (CHANNEL_APP, "APP"),
    (CHANNEL_WAP, "WAP"),
    (CHANNEL_IOS, "IOS"),
    (CHANNEL_ANDROID, "Android"),
    (CHANNEL_UNKNOWN, "未知"),
    (CHANNEL_WEIBO, "微博"),
    (CHANNEL_QQ, "QQ"),
)

REFACTORING_CHANNEL_CHOICES = (
    (CHANNEL_WECHAT, "wechat"),
    (CHANNEL_APP, "web"),
    (CHANNEL_WAP, "wap"),
    (CHANNEL_IOS, "IOS App"),
    (CHANNEL_ANDROID, "Android App"),
    (CHANNEL_UNKNOWN, "未知"),
    (CHANNEL_WEIBO, "weibo"),
)

CHANNEL_TYPES = (
    (CHANNEL_PC, 'channel_pc'),
    (CHANNEL_WECHAT, 'channel_wechat'),
    (CHANNEL_APP, 'channel_app'),
    (CHANNEL_WAP, 'channel_wap'),
    (CHANNEL_IOS, 'channel_ios'),
    (CHANNEL_ANDROID, 'channel_android'),
    (CHANNEL_UNKNOWN, 'channel_unknown'),
    (CHANNEL_WEIBO, 'channel_weibo'),
    (CHANNEL_QQ, 'channel_qq'),
)

# 日志模块
MODULES_MAP = {
    "openstationmanage-detail": "开站管理",
    "openstationmanage-list": "开站管理",
    "openstation-list": "开站管理",
    "industry-list": "客户行业设置",
    "industry-detail": "客户行业设置",
    "openstationmanage-modify-status": "修改状态",
    "server-detail": "经典版服务",
    "server-list": "经典版服务",
    "servergroup-detail": "服务组",
    "servergroup-list": "服务组",
    "grid-detail": "节点",
    "grid-list": "节点",
    "sertype-detail": "经典版产品配置",
    "sertype-list": "经典版产品配置",
    "product-detail": "经典版产品配置",
    "product-list": "经典版产品配置",
    "versioninfo-list": "经典版产品配置",
    "versioninfo-detail": "经典版产品配置",
    "functioninfo-list": "经典版产品配置",
    "functioninfo-detail": "经典版产品配置",
    "singleselection-modify-default": "经典版产品配置",
    "group-detail": "角色权限",
    "group-list": "角色权限",
    "user-detail": "人员配置",
    "user-list": "人员配置",
    "status_create": "订单状态修改",
    "goodsmodel-list": "商品模块",
    "goodsmodel-detail": "商品模块",
    "tagclass-list": "标签模块",
    "tagclass-detail": "标签模块",
    "singlegoods-list": "单品模块",
    "singlegoods-detail": "单品模块",
    "multiplegoods-list": "组合商品模块",
    "multiplegoods-detail": "组合商品模块",
    "advertising_manage-list": "广告模块",
    "advertising_manage-detail": "广告模块",
    "specificationparameter-list": "产品规格参数",
    "specificationparameter-detail": "产品规格参数",
    "ad_put": "广告上架",
    "ad_time": "广告提前上架",
    "get_editor": "富文本上传图片",
    "create_put_up": "商品上架新增&修改",
    "delete_put": "删除下架商品",
    "put_up": "上架操作",
    "put_off": "下架操作",
    "applications.setup.views.login_config": "ldap登录配置",

    "applications.version.views.VersionProductManage": "版本设置",
    "applications.version.views.VersionRepositoryManage": "版本设置",

    "applications.user_manage.views.user_list": "人员设置",
    "applications.user_manage.views.user_detail": "人员设置",
    "applications.user_manage.views.user_add": "人员设置",
    "applications.user_manage.views.user_delete": "人员设置",
    "applications.user_manage.views.user_put": "人员设置",

    "RolesViewSet": "角色权限",
    "RolesDetailSet": "角色权限",

    "list_roles": "角色权限",
    "list_role": "角色权限",
    "list_group_roles": "角色权限",
    "list_role_members": "角色权限",
    "list_user_role": "角色权限",
    "delete_role_members": "角色权限",
    "update_role_members": "角色权限",
    "create_role_members": "角色权限",

    "personal_changepassword": "人员设置",
    "change_role": "角色权限",
    "change_group": "角色权限",

    "home_top": "首页",
    "company_data": "企业数据",
    "versionproduct-detail": "版本管理",

    "applications.data_manage.views_script.test_history_channel": "获取重构版pv, uv",
    "applications.data_manage.views_script.get_consult": "获取经典版pv",
    "applications.data_manage.views_script.get_visitor": "获取经典版uv",
    "applications.data_manage.views_script.update_all_open_station": "校正生态云所有站点",
    "applications.data_manage.views_script.update_grid_open_station": "同步指定节点下站点到生态云",
    "applications.support.views.classic_day_pwd": "经典版系统密码每天变更脚本",
    "applications.support.views.classic_week_pwd": "经典版系统密码每两周变更脚本",
}

# 脚本名称配置
SCRIPT_CONFIGURATION = (
    (0, '获取经典版pv'),
    (1, '获取重构版pv, uv'),
    (2, '同步指定节点下站点到生态云'),
    (3, '校正生态云所有站点'),
    (4, '获取经典版uv'),
    # (5, '经典版系统密码每天变更脚本'),
    # (6, '经典版系统密码每两周变更脚本'),
)

# 日志类型
TYPE_POST = 1
TYPE_DELETE = 2
TYPE_PUT = 3
TYPE_LOGIN = 4
TYPE_LOGOUT = 5
TYPE_VIEW = 6
TYPE_ELSE = 500
SCRIPT = 110
LOG_TYPE_CHOICES = (
    (TYPE_POST, "新增"),
    (TYPE_DELETE, "删除"),
    (TYPE_PUT, "修改"),
    (TYPE_LOGIN, "登录"),
    (TYPE_LOGOUT, "退出"),
    (TYPE_ELSE, "其他"),
    (TYPE_VIEW, "浏览"),
    (SCRIPT, "脚本执行"),
)

ACTION_MAP = {
    "POST": TYPE_POST,
    "PUT": TYPE_PUT,
    "DELETE": TYPE_DELETE,
    "GET": TYPE_VIEW,
    "SCRIPT": SCRIPT,
}

# 运营记录统计
OPERATE_CREATE = 1
OPERATE_RENEWAL = 2
OPERATE_ADD_PRODUCT = 3
OPERATE_ONLINE = 4
OPERATE_OFFLINE = 5
OPERATE_ACTION_CHOICES = (
    (OPERATE_CREATE, "新增客户"),
    (OPERATE_RENEWAL, "续费客户"),
    (OPERATE_ADD_PRODUCT, "新增产品"),
    (OPERATE_ONLINE, "上线客户"),
    (OPERATE_OFFLINE, "下线客户"),
)

# 产品—服务分类
CLASSIC_VERSION = 1
REFACTOR_VERSION = 2
PROD_SERV_VERSIONS = (
    (REFACTOR_VERSION, '重构版'),
    (CLASSIC_VERSION, '经典版')
)

STATUS_OFFLINE = False
STATUS_ONLINE = True
RELEASE_STATUS_TYPES = (
    (STATUS_OFFLINE, "未发版"),
    (STATUS_ONLINE, "发版"),
)

STATUS_OFFLINE = False
STATUS_ONLINE = True
STATUS_TYPES = (
    (STATUS_OFFLINE, "下线"),
    (STATUS_ONLINE, "上线"),
)

# 标签类别
LEBAL_INDUSTRY = 1
LEBAL_CUSTOMER_CASE = 2
LEBAL_PRODUCT = 3
LEBAL_SERVER_SIZE = 4
LEBAL_INQUIRES = 5
LEBAL_ROBOT = 6
TAG_CLASS = (
    (LEBAL_INDUSTRY, '行业'),
    (LEBAL_CUSTOMER_CASE, '客户案例'),
    (LEBAL_PRODUCT, '产品类型'),
    (LEBAL_SERVER_SIZE, '客服规模'),
    (LEBAL_INQUIRES, '咨询量/月'),
    (LEBAL_ROBOT, '机器人'),
)

# 上架状态
PUTAWAY_ON = 1
PUTAWAY_OFF = 2
PUTAWAY_WAIT = 3
PUT_AWAY = (
    (PUTAWAY_ON, '上架'),
    (PUTAWAY_OFF, '下架'),
    (PUTAWAY_WAIT, '待上架'),
)

# 售卖状态
PRESELL = 1
SELL = 2
SELL_STATUS = (
    (PRESELL, '预售'),
    (SELL, '可售卖'),
)

# 是否首页展示
RECOMMEND = 1
NO_RECOMMEND = 2
RECOMMENDATION = (
    (RECOMMEND, '展示'),
    (NO_RECOMMEND, '不展示'),
)

# 订单状态
Financial_Control = 1
OPEN_SITE = 2
Implement = 3
Trade_Successfully = 4
FAILURE = 5
ORDER_STATUS = (
        ("Financial_Control",  "财务审核"),
        ("OPEN_SITE", "开站中"),
        ("Implement", "实施中"),
        ("Trade_Successfully", "交易完成"),
        ("FAILURE", "已失效")
    )

# 商品属性
Single = 1
mulite = 2
GOODS_TYPE = (
    (Single, '单品'),
    (mulite, '组合商品'),
)

# 广告位置
HOME_ROTATION_MAP = 0
LIST_ROTATION_MAP = 1
ADVERTISING_POSITION = (
    (HOME_ROTATION_MAP, "首页轮播图"),
    (LIST_ROTATION_MAP, "列表轮播图"),
)

# 填写控件
INPUT_TEXT = 0
DROP_LIST = 1
FILL_CONTROL = (
    (INPUT_TEXT, "单行文本框"),
    (DROP_LIST, "下拉列表框"),
)


# 服务器分类
KSY_CLOUD = 0
ALI_CLOUD = 1
CLOUD_CLASS = (
    (KSY_CLOUD, "金山云"),
    (ALI_CLOUD, "阿里云")
)

# 登录模式
LDAP = 1
LOCAL = 2
LOCAL_LDAP = 3
LDAP_COCAL = 4
LOGIN_MODEL = (
    (LDAP, "LDAP登录模式"),
    (LOCAL, "本地登录模式"),
    (LOCAL_LDAP, "本地+LDAP模式"),
    (LDAP_COCAL, "LDAP+本地模式"),
)

# 创建来源
LDAP = 1
LOCAL = 2
CREATE_SOURCE = (
                (LDAP, "来自ldap"),
                (LOCAL, "来自本地"),
)

# 客户库备注分类
REMARK_TYPE = (
    (1, "客户库备注"),
    (2, "问题备注"),
    (3, "客户需求沟通结果"),
    (4, "产品配置备注"),
)

# 发送邮件配置
SENDER = 'sport@xiaoneng.cn'
MAIL_HOST = "smtp.exmail.qq.com"
MAIL_USER = "sport@xiaoneng.cn"
MAIL_PASS = "xiaoneng.2015"

GRID = 1
GRID1 = 2
GRID2 = 3
GRID3 = 4
GRID4 = 5
VERSION_ID = (
    (GRID, 'grid'),
    (GRID1, 'grid1'),
    (GRID2, 'grid2'),
    (GRID3, 'grid3'),
    (GRID4, 'grid4'),
)

MAIN_TJ = ["sh", "sz", "Za", "上海", "北京", "hz", "mo", "re", "ha"]

# ZABBIX节点状态
Z_C = 1
J_G = 2
Y_Z = 3
GRID_STATUS = (
    (Z_C, "正常"),
    (J_G, "警告"),
    (Y_Z, "严重"),
)

# ZABBIX监控项
key_dict = {"vm.memory.size[available]": "系统可用内存",
               "system.cpu.util[,idle]":"cpu可用使用率", "system.cpu.util[,iowait]": "cpu等待",
               "system.cpu.load[percpu,avg1]": "一分钟负载",
               "vfs.fs.size[/opt,free]": "opt可用", "vfs.fs.size[/,free]": "根可用",
               "vfs.fs.size[/opt,total]": "opt总容量", "vfs.fs.size[/,total]": "根总容量"}

# 节点状态字典
status_dict = {1: "正常", 2: "告警", 3: "灾难"}

# 1G内存数值
one_g = 1024 ** 3
m_500 = one_g / 2
m_300 = one_g / 10 * 3

# 开站导出表头字典
title_dict = {
    "id": "序号",
    "online_status": "状态",
    "company_info__station_type": "站点类型",
    "company_info__industry__industry": "行业",
    "company_info__company_name": "客户名称",
    "station_info__company_id": "客户ID",
    "station_info__grid__grid_name": "节点",
    "station_info__classify": "产品分类",
    "station_info__deploy_way": "部署方式",
    "station_info__cli_version": "客户版本",
    "station_info__open_station_time": "开站时间",
    "station_info__close_station_time": "到期日",
    "station_info__order_work": "信息来源"
}


URL = ['bj-slb-ha', 'sh-slb-ha']

HOST_DICT = {
    "bj-ali-g1-zabbix_proxy-01": "北京BGP",
    "bj-ksy-v0-network-01": "北京电信",
    "bj-ksy-v0-network-02": "北京联通",
    "sh-ksy-v0-network-01": "上海电信",
    "sh-ksy-v0-network-02": "上海联通",
    "hz-ali-g1-zabbix_proxy-01": "杭州BGP",
    "sz-ksy-v0-network-01": "深圳BGP",
}

# EMAIL
EMAIL_USERNAME = 'trigger@email.ntalker.com'
EMAIL_PWD = '8ql6yhYRl177'

EMAIL_LIST = {
    "测试账户": 'yinzhiqiang@xiaoneng.cn',
    "营销中心": 'yingxiaozhongxin@xiaoneng.cn',
    "研发中心": 'rdcenter@ntalker.cn',
    "交付中心（所有人）": 'delivery@xiaoneng.cn',
    "客户运营中心（CSC）（所有人）": 'supports@xiaoneng.cn',
    "人事行政部（所有人）": 'hrall@xiaoneng.cn',
}

#SMS
SMSNAME = 'interface'
SMSPWD = '8d989a2a09'
SMSSCORPID = '11999'
SMSTARGET = 'https://seccf.51welink.com/submitdata/service.asmx'
SMSSPRDID = '1012818'


# 培训管理问题类型
TRAIN = 1
MATTER_TYPE = (
    (TRAIN, '培训'),
)

# 培训管理问题状态
MATTER_STATUS = (
    (1, "培训信息提交"),
    (2, "讲师分配完成"),
    (3, "驳回"),
    (4, "培训需求确认完成"),
    (5, "培训准备完成"),
    (6, "培训挂起"),
    (7, "终止培训"),
    (8, "培训完成"),
    (9, "交接完成"),
    (10, "遗留问题已确认"),
    (11, "调查人员已分配"),
    (12, "培训任务完成"),
)

# 是否有遗留问题
Y_NLEGACY = (
    (1, "有遗留问题"),
    (0, "没有遗留问题"),
)

# 培训管理培训方式
TRAINING_METTART_METHOD = (
    (0, '无'),
    (1, '远程'),
    (2, '现场'),
)

# 问题满意度等级
SATISFACTION_SURVEY = (
    (5, "非常满意"),
    (4, "满意"),
    (3, "一般"),
    (2, "不满意"),
    (1, "非常不满意"),
)

WAY_MATTERCOMMUNICATE = (
    (0, "电话"),
    (1, "QQ"),
    (2, "微信"),
    (3, "现场"),
    (4, "邮件"),
    (5, "钉钉"),
    (6, "其他"),
)

# 附件类型
ATTACHMENT_TYPE = (
    (1, "培训管理"),
    (2, "产品配置")
)

# 驳回理由类型
REJECT_TYPE = (
    (1, "培训管理"),
    (2, "产品配置"),
    (3, "操作方不通过原因"),
    (4, "需求方不通过原因"),
)

# 问题配置状态
PRODUCT_STATUS = (
    (3, "任务审核中"),
    (4, "云平台操作中"),
    (5, "云平台操作完成"),
    (6, "运维操作中"),
    (7, "运维操作完成"),
    (8, "操作方验证中"),
    (9, "需求方验证中"),
    (10, "验证通过"),
    (11, "任务关闭"),
    (12, "已驳回"),
)

# 产品配置所属模块
Subordinate_Module = (
    (0, '无'),
    (1, '线上功能'),
    (2, '设置'),
    (3, '接口'),
    (4, '机器人'),
    (5, '集成对接'),
    (6, '互动记录'),
    (7, '我的同事'),
    (8, '工单/用户资源'),
    (9, '呼叫中心'),
    (10, 'XBot机器人(本地部署版)'),
    (11, 'KPI报表'),
    (12, '轨迹'),
    (13, '访客端'),
    (14, '留言飞语'),
    (15, '渠道API'),
    (16, '服务器（T2D&Tchat）'),
    (17, '微信'),
    (18, '客户端'),
    (19, '实时监控'),
    (20, '前端实施'),
    (21, '兼容性测试'),
    (22, '二维码'),
    (23, 'WAP-安卓'),
    (24, 'WAP-iOS'),
    (25, 'SDK-IOS'),
    (26, 'SDK-Android'),
    (27, 'JS'),
    (28, 'APP'),
    (29, 'API接口'),
)
# 版本管理经典版产品
version_classic = ['经典-在线咨询', '经典-呼叫中心', '经典-智能工单', '经典-智能机器人', '经典-CRM', '经典-互动记录', '经典-数据洞察', '经典-SDK']
# 版本管理重构版产品
version_pro = ['重构-在线咨询', '重构-呼叫中心', '重构-智能工单', '重构-智能机器人', '重构-CRM', '重构-互动记录', '重构-数据洞察', '重构-SDK', '运营平台']