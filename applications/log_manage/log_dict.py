from applications.production_manage.models import Product
from applications.workorder_manage.models import Matter

# 开站字段中英文dict
openstation_dict = {
    "company_name": "公司名称",
    "station_type": "站点类型",
    "industry": "行业",
    "company_email": "公司邮箱",
    "abbreviation": "公司简称",
    "GSZZ": "营业执照名称",
    "customer_type": "客户类型",
    "service_area": "服务区域",
    "cli_version": "客户版本",
    "deploy_way": "部署方式",
    "classify": "产品分类",
    "validity_days": "开站有效期",
    "grid": "节点名称",
    "open_station_time": "开站日期",
    "version_id": "version_id",
    "close_station_time": "站点关闭日期",
    "sales": "销售人员",
    "pre_sales": "售前人员",
    "oper_cslt": "运营顾问",
    "impl_cslt": "实施顾问",
    "oper_supt": "运营支持",
    "company_address": "公司地址",
    "company_url": "公司url",
    "brand_effect": "品牌效应",
    "comment": "驳回理由",
    "consult": "PV / 天",
    "customer_level": "客户级别",
    "kf_number": "坐席数",
    "amount_cashed": "回款金额",
    "contract_accessory": "附件",
    "cashed_time": "回款时间",
    "contract_amount": "合同金额",
    "contract_content": "功能模块",
    "contract_end_time": "合同结束时间",
    "contract_index": "合同编号",
    "contract_start_time": "合同开始时间",
    "platform_informatiom": "平台信息",
    "sign_contract": "是否签署合同",
    "special_selection": "是否已特批",
    "training_method": "培训方式",
    "transmitting_state": "流转状态",
    "visitor": " UV / 天",
    "link_type": "联系人类别",
    "link_email": "电子邮箱",
    "link_phone": "联系电话",
    "link_qq": "QQ号",
    "link_work": "联系人职务",
    "linkman": "联系人",
    "link_info": "联系人信息",
}


def get_product():
    """
    获取产品
    :return:
    """
    product_dict = {}
    queryset = Product.objects.all()
    for p in queryset:
        product_dict.update({p.id: p.product})
    return product_dict


# 日志列表操作类型
operation_type = {
    "data": [{
        "name": "首页",
        "value": "date_overview",
        "children": []
    },
        {
            "name": "监控大屏",
            "value": "supervisory_control",
            "children": []
        },
        {
            "name": "客户管理",
            "value": "cutom_manage",
            "children": [{
                "name": "客户库",
                "value": "KHK",
                "children": []
            },
                {
                    "name": "待审批",
                    "value": "pending",
                    "children": []
                },
                {
                    "name": "开站管理",
                    "value": "open_station",
                    "children": []
                }
            ]
        },
        {
            "name": "运维管理",
            "value": "operations_management",
            "children": [{
                "name": "经典版服务 ",
                "value": "classic_service ",
                "children": []
            }, {
                "name": "服务组",
                "value": "service_group",
                "children": []
            },
                {
                    "name": "节点",
                    "value": "grid",
                    "children": []
                }
            ]
        }, {
            "name": "产品管理",
            "value": "product_management",
            "children": [{
                "name": "经典版产品配置",
                "value": "classic_product ",
                "children": []
            }, {
                "name": "重构版产品配置",
                "value": "rec_product",
                "children": []
            }]
        }, {
            "name": "数据统计",
            "value": "data_statistics",
            "children": [{
                "name": "企业数据",
                "value": "company_date",
                "children": []
            },
                {
                    "name": "渠道统计",
                    "value": "channel_date",
                    "children": []
                },
                {
                    "name": "节点统计",
                    "value": "gride_date",
                    "children": []
                },
                {
                    "name": "站点统计",
                    "value": "station_data",
                    "children": []
                },
                {
                    "name": "行业统计",
                    "value": "industry_data",
                    "children": []
                }
            ]
        }, {
            "name": "账户管理",
            "value": "account",
            "children": [{
                "name": "角色权限",
                "value": "group_permission ",
                "children": []
            }, {
                "name": "人员设置",
                "value": "person_set",
                "children": []
            }]
        }, {
            "name": "版本管理",
            "value": "version_manage",
            "children": [{
                "name": "版本设置 ",
                "value": "version_set ",
                "children ": []
            }]
        }, {
            "name": "设置",
            "value": "set_up",

            "children": [{
                "name": "登录模式设置 ",
                "value": "login_set ",
                "children": []
            }, {
                "name": "客户行业设置",
                "value": "custom_set",
                "children": []
            },
                {
                    "name": "帮助中心设置",
                    "value": "help_set",
                    "children": []
                }
            ]
        }

    ]
}


# 日志字段变更表
log_str_change = {
    "工单管理-开站管理": "开站管理",

    "设置-客户行业": "客户行业设置",

    "工单管理-修改状态": "修改状态",

    "产品管理-运维配置-服务器": "经典版服务",

    "产品管理-运维配置-服务组": "服务组",

    "产品管理-运维配置-节点": "节点",

    "产品管理-产品配置": "经典版产品配置",

    "产品管理-版本": "经典版产品配置",

    "权限和人员管理-角色权限": "角色权限",

    "权限和人员管理-人员配置": "人员配置",

    "版本产品模块": "版本设置",

    "版本库模块": "版本设置",

    "查看用户列表": "人员设置",

    "查看用户详情": "人员设置",

    "用户新增": "人员设置",
    "用户删除": "人员设置",
    "用户修改": "人员设置",

    "系统列表": "角色权限",
    "系统删除": "角色权限",

    "展示角色类别": "角色权限",
    "展示角色": "角色权限",
    "展示角色组": "角色权限",
    "删除角色成员": "角色权限",
    "添加角色成员": "角色权限",
    "修改个人密码": "人员设置",
    "修改系统名称": "角色权限"
}


# 客户库数字选项对照表
khk_num = {"brand_effect": {1: "世界500强", 2: "中国500强", 3: "行业前十", 0: "无"},
           "classify": {1: "经典版", 2: "重构版"},
           "cli_version": {1: "B2B", 2: "B2C", 4: "B2B2C", 3: "不限"},
           "customer_level": {0: "无", 1: "A", 2: "B", 3: "C"},
           "customer_type": {"False": "新客户", "True": "老客户"},
           "deploy_way": {1: "标准版", 2: "公有云", 3: "专属云", 4: "私有云", 5: "缺省"},
           "sign_contract": {0: "否", 1: "是"},
           "link_type": {1: "客户方业务", 2: "客户方项目", 3: "客户方技术", 4: "商务（小能）"},
           "special_selection": {0: "否", 1: "是"},
           "training_method": {0: "无", 1: "远程", 2: "现场", 3: "远程+现场"}
           }


# 培训管理字段对照表
def matter_word(models):
    matter_dict = {}
    # 获取matter一个实例
    matter = models.objects.all().first()
    field = matter._meta.fields
    for f in field:
        matter_dict.update({f.name: f.verbose_name})
    return matter_dict


# 版本管理状态对照
version_dict = {
    '0': "初始",
    '1': "通过",
    '2': "驳回",
    '3': "被驳回",
    '4': "冒烟通过"

}