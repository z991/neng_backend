import logging

from django.contrib.auth.models import Group, Permission, User
from rest_framework import serializers
from applications.setup.models import LoginLdapConfig
from applications.permission_and_staff_manage.models import Structure, Employee
from libs.login_set import get_login_model
from ldap_server.ldap_config import login_model

log = logging.getLogger("Django")


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'content_type')


class GroupForUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class SimpGroupFromLdapSerializer(serializers.ModelSerializer):
    def get_own_user_count(self, group):
        # login_model = LoginLdapConfig.objects.all().values_list('login_model', flat=True)
        if login_model == 3 or login_model == 4:
            count = group.user_set.count()
        else:
            count = group.user_set.filter(user_profile__create_source=login_model).count()
        return count

    own_user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'name', 'own_user_count')


class GroupFromLdapSerializer(serializers.ModelSerializer):
    PERMS_MAP = {
        "GROUP_PERMS": {
            "modify": ("change_group", "add_group"),
            "delete": "delete_group",
            "view": "view_group"
        },
        "USER_PERMS": {
            "modify": ("change_user", "add_user"),
            "delete": "delete_user",
            "view": "view_user"
        },
        "STRUCTURE_PERMS": {
            "modify": ("change_structure", "add_structure"),
            "delete": "delete_structure",
            "view": "view_structure"
        },
        "GRID_PERMS": {
            "modify": ("change_grid", "add_grid"),
            "delete": "delete_grid",
            "view": "view_grid"},
        "SER-GRP_PERMS": {
            "modify": ("change_servergroup", "add_servergroup"),
            "delete": "delete_servergroup",
            "view": "view_servergroup"},
        "SERVER_PERMS": {
            "modify": ("change_server", "add_server"),
            "delete": "delete_server",
            "view": "view_server"},
        "REF-SERVER_PERMS": {
            "modify": ("change_server", "add_server"),
            "delete": "delete_server",
            "view": "view_server"},

        "REF-PRO_PERMS": {
            "modify": ('add_versioninfo', 'change_versioninfo',
                       'add_product', 'change_product',
                       'add_singleselection', "change_singleselection",
                       'add_functioninfo', "change_functioninfo"),
            "delete": ("delete_versioninfo", "delete_product",
                       "delete_singleselection", "delete_functioninfo"),
            "view": ("view_versioninfo", "view_product",
                     "view_singleselection", "view_product")
        },
        "PRO_PERMS": {
            "modify": ('add_versioninfo', 'change_versioninfo',
                       'add_product', 'change_product',
                       'add_singleselection', "change_singleselection",
                       'add_functioninfo', "change_functioninfo"),
            "delete": ("delete_versioninfo", "delete_product",
                       "delete_singleselection", "delete_functioninfo"),
            "view": ("view_versioninfo", "view_product",
                     "view_singleselection", "view_product")
        },

        "OPEN_STATION_PERMS": {
            "modify": ("change_openstationmanage", "add_openstationmanage"),
            "delete": "delete_openstationmanage",
            "view": "view_openstationmanage"
        },
        "CUSTOMER-KHK_PERMS": {
            "modify": ("change_customer-khk", "add_customer-khk"),
            "delete": "delete_customer-khk",
            "view": "view_customer-khk"
        },
        "SYSTEM_LOG_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_system-log",
        },
        "PERSONAL_LOG_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_personal-log",
        },

        "PANDECT_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_pandect",
        },
        "CHANNEL-INQUIRIES_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_channel-inquiries",
        },
        "CUSTOMER-USE_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_customer-use",
        },
        "GRID-INQUIRIES_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_grid-inquiries",
        },
        "SERGRP-INQUIRIES_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_sergrp-inquiries",
        },
        "ONLINE-CLIENT_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_online-client",
        },
        "ONLINE-PRODUCT_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_online-product",
        },
        "SITE-OPER_PERMS": {
            "modify": 0,
            "delete": 0,
            "view": "view_site-oper",
        },

        "SETUP_HELP_CENTER": {
            "modify": ("add_sitereceptiongroup", "change_sitereceptiongroup"),
            "delete": "delete_sitereceptiongroup",
            "view": "view_sitereceptiongroup",
        },
        "SETUP_INDUSTRY": {
            "modify": ("add_industry", "change_industry"),
            "delete": "delete_industry",
            "view": "view_industry",
        },
        "SETUP_SYSTEM_USER": {
            "modify": ("add_system_user", "change_system_user"),
            "delete": "delete_system_user",
            "view": "view_system_user",
        },
        "SETUP_SYSTEM_ROLE": {
            "modify": ("add_role", "change_role"),
            "delete": "delete_role",
            "view": "view_role",
        },
        "SETUP_LOGINCONFIG_PERMS": {
            "modify": "change_loginconfig",
            "delete": 0,
            "view": "view_loginconfig",
        },
        "SETUP_USERSET": {
            "modify":  ("add_userset", "change_userset"),
            "delete": "delete_userset",
            "view": "view_userset",
        },

        "SINGLE_GOODS_PERMS": {
            "modify": ("change_singlegoods", "add_singlegoods"),
            "delete": "delete_singlegoods",
            "view": "view_singlegoods"
        },
        "ADVERTISING_PERMS": {
            "modify": ("change_advertising", "add_advertising"),
            "delete": "delete_advertising",
            "view": "view_advertising"
        },
        "MULTIPLEGOODS_PERMS": {
            "modify": ("change_multiplegoods", "add_multiplegoods"),
            "delete": "delete_multiplegoods",
            "view": "view_multiplegoods"
        },
        "PUTAWAY_PERMS": {
            "modify": ("change_putaway", "add_putaway"),
            "delete": "delete_putaway",
            "view": "view_putaway"
        },
        "GOODSMODEL_PERMS": {
            "modify": ("change_goodsmodel", "add_goodsmodel"),
            "delete": "delete_goodsmodel",
            "view": "view_goodsmodel"
        },
        "GOODSCLASS_PERMS": {
            "modify": ("change_tagclass", "add_tagclass"),
            "delete": "delete_tagclass",
            "view": "view_tagclass"
        },

        "ORDER_INFO_PERMS": {
            "modify": "change_orderinfo",
            "delete": 0,
            "view": "view_orderinfo"
        },
        "DATA_OVERVIEW": {
            "modify": 0,
            "delete": 0,
            "view": "view_data-overview"
        },
        "COMPANY_INQUIRE": {
            "modify": 0,
            "delete": 0,
            "view": "view_company-inquire"
        },
        "CHANNEL_INQUIRE": {
            "modify": 0,
            "delete": 0,
            "view": "view_channel-inquire"
        },
        "GRID_INQUIRE": {
            "modify": 0,
            "delete": 0,
            "view": "view_grid-inquire"
        },
        "INDUSTRY_INQUIRE": {
            "modify": 0,
            "delete": 0,
            "view": "view_site-industry"
        },

        "VERSION_PERMS": {
            "modify": ("change_versionrepository", "add_versionrepository",
                       "change_versionproduct", "add_versionproduct"),
            "delete": ("delete_versionrepository", "delete_versionproduct"),
            "view": ("view_versionrepository", "view_versionproduct"),
        },
        "SUPPORT": {
            "modify": 0,
            "delete": 0,
            "view": "view_support"
        },
        # "VERSION_PRODUCT_PERMS": {
        #     "modify": (),
        #     "delete": "",
        #     "view": ""
        # },
    }

    def get_permissions(self, group):
        permission_list = group.permissions.all().values_list("codename", flat=True)
        # param perms: codename， 或者包含codename的元祖
        # 检测是否拥有权限， 如果传入codename元祖，则拥有其中任一权限，则认为拥有权限（或关系）
        def has_perm(perms):
            if isinstance(perms, tuple):
                for perm in perms:
                    if perm in permission_list:
                        return 1
                return 0
            else:
                if perms in permission_list:
                    return 1
                return 0

        perm_dict = {
            'auth': {
                'view': 0,
                'group': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["GROUP_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["GROUP_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["GROUP_PERMS"]['view']),
                },
                'user': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["USER_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["USER_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["USER_PERMS"]['view']),
                },
                'structure': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["STRUCTURE_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["STRUCTURE_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["STRUCTURE_PERMS"]['view']),
                }
            },

            'version_manage': {
                'view': 0,
                'repository': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["VERSION_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["VERSION_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["VERSION_PERMS"]['view']),
                },
                # 'versionproduct': {
                #     "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["VERSION_PRODUCT_PERMS"]['modify']),
                #     "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["VERSION_PRODUCT_PERMS"]['delete']),
                #     "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["VERSION_PRODUCT_PERMS"]['view']),
                # },
            },

            'pro': {
                'view': 0,
                'ref-product': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['modify']),
                                "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['delete']),
                                "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['view'])},
                'product': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["PRO_PERMS"]['modify']),
                            "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["PRO_PERMS"]['delete']),
                            "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["PRO_PERMS"]['view'])}
            },
            'ops': {
                'view': 0,
                'server': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERVER_PERMS"]['modify']),
                           "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERVER_PERMS"]['delete']),
                           "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERVER_PERMS"]['view'])},
                'ser-grp': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SER-GRP_PERMS"]['modify']),
                            "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SER-GRP_PERMS"]['delete']),
                            "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SER-GRP_PERMS"]['view'])},
                'grid': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID_PERMS"]['modify']),
                         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID_PERMS"]['delete']),
                         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID_PERMS"]['view'])},
            },
            # 'production_manage': {
            #     'view': 0,
            #     'ops': {
            #         'view': 0,
            #         'ref-server': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-SERVER_PERMS"]['modify']),
            #                        "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-SERVER_PERMS"]['delete']),
            #                        "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-SERVER_PERMS"]['view'])},
            #         'server': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERVER_PERMS"]['modify']),
            #                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERVER_PERMS"]['delete']),
            #                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERVER_PERMS"]['view'])},
            #         'ser-grp': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SER-GRP_PERMS"]['modify']),
            #                     "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SER-GRP_PERMS"]['delete']),
            #                     "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SER-GRP_PERMS"]['view'])},
            #         'grid': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID_PERMS"]['modify']),
            #                  "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID_PERMS"]['delete']),
            #                  "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID_PERMS"]['view'])},
            #     },
            #     'pro': {
            #         'view': 0,
            #         'ref-product': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['modify']),
            #                         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['delete']),
            #                         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"]['view'])},
            #         'product': {"modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["PRO_PERMS"]['modify']),
            #                     "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["PRO_PERMS"]['delete']),
            #                     "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["PRO_PERMS"]['view'])}
            #     }
            # },
            'workorder_manage': {
                'view': 0,
                'openstationmanage': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["OPEN_STATION_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["OPEN_STATION_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["OPEN_STATION_PERMS"]['view']),
                },
                'customer-khk': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["CUSTOMER-KHK_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["CUSTOMER-KHK_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["CUSTOMER-KHK_PERMS"]['view']),
                }
            },
            'log': {
                'view': 0,
                'system-log': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SYSTEM_LOG_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SYSTEM_LOG_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SYSTEM_LOG_PERMS"]['view']),
                },
                'personal-log': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"]['view']),
                }
            },
            # 'data_manage': {
            #     'view': 0,
            #     'pandect': {
            #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["PANDECT_PERMS"]['modify']),
            #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["PANDECT_PERMS"]['delete']),
            #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["PANDECT_PERMS"]['view']),
            #     },
            #     'prod_oper': {
            #         'view': 0,
            #         "channel-inquiries": {
            #             "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["CHANNEL-INQUIRIES_PERMS"]['modify']),
            #             "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["CHANNEL-INQUIRIES_PERMS"]['delete']),
            #             "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["CHANNEL-INQUIRIES_PERMS"]['view']),
            #         },
            #         "customer-use": {
            #             "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["CUSTOMER-USE_PERMS"]['modify']),
            #             "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["CUSTOMER-USE_PERMS"]['delete']),
            #             "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["CUSTOMER-USE_PERMS"]['view']),
            #         },
            #         "online-client": {
            #             "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["ONLINE-CLIENT_PERMS"]['modify']),
            #             "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["ONLINE-CLIENT_PERMS"]['delete']),
            #             "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["ONLINE-CLIENT_PERMS"]['view']),
            #         },
            #         "online-product": {
            #             "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["ONLINE-PRODUCT_PERMS"]['modify']),
            #             "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["ONLINE-PRODUCT_PERMS"]['delete']),
            #             "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["ONLINE-PRODUCT_PERMS"]['view']),
            #         },
            #         "site-oper": {
            #             "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SITE-OPER_PERMS"]['modify']),
            #             "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SITE-OPER_PERMS"]['delete']),
            #             "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SITE-OPER_PERMS"]['view']),
            #         },
            #     },
            #
            #     'data_ops': {
            #         'view': 0,
            #         "grid-inquiries": {
            #             "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID-INQUIRIES_PERMS"]['modify']),
            #             "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID-INQUIRIES_PERMS"]['delete']),
            #             "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID-INQUIRIES_PERMS"]['view']),
            #         },
            #         "sergrp-inquiries": {
            #             "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERGRP-INQUIRIES_PERMS"]['modify']),
            #             "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERGRP-INQUIRIES_PERMS"]['delete']),
            #             "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SERGRP-INQUIRIES_PERMS"]['view']),
            #         }
            #
            #     }
            #
            # },
            'data_manage': {
                'view': 0,
                'company-inquire': {
                    "modify": 0,
                    "delete": 0,
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["COMPANY_INQUIRE"]['view']),
                },
                'channel-inquire': {
                    "modify": 0,
                    "delete": 0,
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["CHANNEL_INQUIRE"]['view']),
                },
                'grid-inquire': {
                    "modify": 0,
                    "delete": 0,
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["GRID_INQUIRE"]['view']),
                },
                'site-industry': {
                    "modify": 0,
                    "delete": 0,
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["INDUSTRY_INQUIRE"]['view']),
                },
            },

            'setup': {
                'view': 0,
                'help_center': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_HELP_CENTER"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_HELP_CENTER"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_HELP_CENTER"]['view']),
                },
                'industry': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_INDUSTRY"]['modify']),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_INDUSTRY"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_INDUSTRY"]['view']),
                },
                # 'system_setting': {
                #     "view": 0,
                #     "role": {
                #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_SYSTEM_ROLE"]['modify']),
                #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_SYSTEM_ROLE"]['delete']),
                #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_SYSTEM_ROLE"]['view']),
                #     },
                #     "system_user": {
                #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_SYSTEM_USER"]['modify']),
                #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_SYSTEM_USER"]['delete']),
                #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_SYSTEM_USER"]['view']),
                #     },
                # },
                'loginconfig': {
                    "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_LOGINCONFIG_PERMS"]["modify"]),
                    "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_LOGINCONFIG_PERMS"]['delete']),
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_LOGINCONFIG_PERMS"]['view']),
                },
                # 'userset': {
                #     "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_USERSET"]["modify"]),
                #     "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_USERSET"]['delete']),
                #     "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SETUP_USERSET"]['view']),
                # },
            },
            # 'goods_manage': {
            #     'view': 0,
            #     'tagclass': {
            #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["GOODSCLASS_PERMS"]['modify']),
            #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["GOODSCLASS_PERMS"]['delete']),
            #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["GOODSCLASS_PERMS"]['view'])},
            #     'goodsmodel': {
            #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["GOODSMODEL_PERMS"]['modify']),
            #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["GOODSMODEL_PERMS"]['delete']),
            #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["GOODSMODEL_PERMS"]['view'])},
            #     'putaway': {
            #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["PUTAWAY_PERMS"]['modify']),
            #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["PUTAWAY_PERMS"]['delete']),
            #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["PUTAWAY_PERMS"]['view'])},
            #     'singlegoods': {
            #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["SINGLE_GOODS_PERMS"]['modify']),
            #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["SINGLE_GOODS_PERMS"]['delete']),
            #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SINGLE_GOODS_PERMS"]['view'])},
            #     'multiplegoods': {
            #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["MULTIPLEGOODS_PERMS"]['modify']),
            #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["MULTIPLEGOODS_PERMS"]['delete']),
            #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["MULTIPLEGOODS_PERMS"]['view'])},
            #     'advertising': {
            #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["ADVERTISING_PERMS"]['modify']),
            #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["ADVERTISING_PERMS"]['delete']),
            #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["ADVERTISING_PERMS"]['view']),}
            #     },
            # 'order_info_manage': {
            #     'view': 0,
            #     'orderinfo': {
            #         "modify": has_perm(GroupFromLdapSerializer.PERMS_MAP["ORDER_INFO_PERMS"]['modify']),
            #         "delete": has_perm(GroupFromLdapSerializer.PERMS_MAP["ORDER_INFO_PERMS"]['delete']),
            #         "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["ORDER_INFO_PERMS"]['view']),
            #     }
            # },
            'data_overview': {
                'view': 0,
                'data-overview': {
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["DATA_OVERVIEW"]['view']),
                }
            },
            'operatingtools':{
                'view': 0,
                'support': {
                    "view": has_perm(GroupFromLdapSerializer.PERMS_MAP["SUPPORT"]['view'])
                }
            }
        }
        # 修改二级模块儿查看权限
        for first, second in perm_dict.items():
            for key, options in second.items():
                if isinstance(options, dict):
                    for l_key, l_option in options.items():
                        if isinstance(l_option, dict):
                            if l_option.get('view') == 1:
                                perm_dict[first][key]["view"] = 1
                                break

        # 修改一级模块的查看权限
        for first, second in perm_dict.items():
            for key, options in second.items():
                if isinstance(options, dict):
                    if options.get("view") == 1:
                        perm_dict[first]["view"] = 1
                        break
        return perm_dict

    def get_own_user(self, group):
        # login_model = LoginLdapConfig.objects.all().values_list('login_model', flat=True)
        if login_model == 3 or login_model == 4:
            own_user = group.user_set.all()\
                .values_list("id", "last_name", "employee__department__dpt_name", "user_profile__create_source")
        else:
            own_user = group.user_set.all().filter(user_profile__create_source=login_model)\
            .values_list("id", "last_name", "employee__department__dpt_name", "user_profile__create_source")
        user_list = []
        for id, username, department, source in own_user:
            user_list.append({
                "id": id,
                "user_name": username,
                "department": department,
                "source": source
            })
        return user_list

    def get_own_user_count(self, group):
        # login_model = LoginLdapConfig.objects.all().values_list('login_model', flat=True)
        if login_model == 3 or login_model == 4:
            count = group.user_set.count()
        else:
            count = group.user_set.filter(user_profile__create_source=login_model).count()
        return count

    permissions = serializers.SerializerMethodField()
    own_user = serializers.SerializerMethodField()
    own_user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', 'own_user', 'own_user_count')

    def set_permissions(self, instance, validated_data):
        # param name: json数据中对应模块的名称
        # param perm_map: 在类中指定的权限列表

        def to_new_permissions(name, perm_map):
            for action in ['modify', 'delete', 'view']:
                if formatted_data[name].get(action, 0):
                    if isinstance(perm_map[action], tuple):
                        new_permissions.update(perm_map[action])
                    else:
                        new_permissions.add(perm_map[action])

        # 将前端传来的数据格式化，剔除冗余数据，只保留二级,或三级 模块的权限信息
        def get_formatted_data():
            formatted = dict()
            for each in validated_data.values():
                for key, value in each.items():  # 二级模块
                    # key help_center value {'view': 1, 'delete': 1, 'modify': 1}
                    # 'goodsmodel' 'tagclass'
                    # {'view': 1,'delete': 1,'modify': 1}==value
                    if isinstance(value, dict):
                        """
                        value:{'view': 1}
                        或者
                        value:{'grid': {'view': 0, 'delete': 0, 'modify': 0}, 
                            'ser-grp': {'view': 0, 'delete': 0, 'modify': 0}, 
                            'server': {'view': 0, 'delete': 0, 'modify': 0}, 
                            'ref-server': {'view': 0, 'delete': 0, 'modify': 0}}
                        """
                        for s_key, s_value in value.items():  # 三级模块
                            # s_key == view ,modify
                            # 1,1 == s_value
                            if isinstance(s_value, dict):
                                formatted.update({s_key: s_value})
                            else:
                                formatted.update({key: value})
            return formatted

        formatted_data = get_formatted_data()
        new_permissions = set()  # 前端传来的新权限列表

        # 指定二级模块的名称，以及该二级模块拥有的权限列表，添加至new_permissions
        to_new_permissions("user", GroupFromLdapSerializer.PERMS_MAP["USER_PERMS"])
        to_new_permissions("group", GroupFromLdapSerializer.PERMS_MAP["GROUP_PERMS"])
        to_new_permissions("structure", GroupFromLdapSerializer.PERMS_MAP["STRUCTURE_PERMS"])
        to_new_permissions("server", GroupFromLdapSerializer.PERMS_MAP["SERVER_PERMS"])
        to_new_permissions("ser-grp", GroupFromLdapSerializer.PERMS_MAP["SER-GRP_PERMS"])
        to_new_permissions("grid", GroupFromLdapSerializer.PERMS_MAP["GRID_PERMS"])
        to_new_permissions("ref-product", GroupFromLdapSerializer.PERMS_MAP["REF-PRO_PERMS"])
        to_new_permissions("product", GroupFromLdapSerializer.PERMS_MAP["PRO_PERMS"])
        to_new_permissions("openstationmanage", GroupFromLdapSerializer.PERMS_MAP["OPEN_STATION_PERMS"])
        to_new_permissions("customer-khk", GroupFromLdapSerializer.PERMS_MAP["CUSTOMER-KHK_PERMS"])
        to_new_permissions("system-log", GroupFromLdapSerializer.PERMS_MAP["SYSTEM_LOG_PERMS"])
        to_new_permissions("personal-log", GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"])
        to_new_permissions("personal-log", GroupFromLdapSerializer.PERMS_MAP["PERSONAL_LOG_PERMS"])
        # 版本权限设置
        to_new_permissions("repository", GroupFromLdapSerializer.PERMS_MAP["VERSION_PERMS"])
        # to_new_permissions("versionproduct", GroupFromLdapSerializer.PERMS_MAP["VERSION_PRODUCT_PERMS"])

        # to_new_permissions("pandect", GroupFromLdapSerializer.PERMS_MAP["PANDECT_PERMS"])
        # to_new_permissions("channel-inquiries", GroupFromLdapSerializer.PERMS_MAP["CHANNEL-INQUIRIES_PERMS"])
        # to_new_permissions("customer-use", GroupFromLdapSerializer.PERMS_MAP["CUSTOMER-USE_PERMS"])
        # to_new_permissions("grid-inquiries", GroupFromLdapSerializer.PERMS_MAP["GRID-INQUIRIES_PERMS"])
        # to_new_permissions("sergrp-inquiries", GroupFromLdapSerializer.PERMS_MAP["SERGRP-INQUIRIES_PERMS"])
        # to_new_permissions("online-client", GroupFromLdapSerializer.PERMS_MAP["ONLINE-CLIENT_PERMS"])
        # to_new_permissions("online-product", GroupFromLdapSerializer.PERMS_MAP["ONLINE-PRODUCT_PERMS"])
        # to_new_permissions("site-oper", GroupFromLdapSerializer.PERMS_MAP["SITE-OPER_PERMS"])
        to_new_permissions("company-inquire", GroupFromLdapSerializer.PERMS_MAP["COMPANY_INQUIRE"])
        to_new_permissions("channel-inquire", GroupFromLdapSerializer.PERMS_MAP["CHANNEL_INQUIRE"])
        to_new_permissions("grid-inquire", GroupFromLdapSerializer.PERMS_MAP["GRID_INQUIRE"])
        to_new_permissions("site-industry", GroupFromLdapSerializer.PERMS_MAP["INDUSTRY_INQUIRE"])

        to_new_permissions("help_center", GroupFromLdapSerializer.PERMS_MAP["SETUP_HELP_CENTER"])
        to_new_permissions("industry", GroupFromLdapSerializer.PERMS_MAP["SETUP_INDUSTRY"])
        # to_new_permissions("system_user", GroupFromLdapSerializer.PERMS_MAP["SETUP_SYSTEM_USER"])
        # to_new_permissions("role", GroupFromLdapSerializer.PERMS_MAP["SETUP_SYSTEM_ROLE"])
        to_new_permissions("loginconfig", GroupFromLdapSerializer.PERMS_MAP["SETUP_LOGINCONFIG_PERMS"])
        # to_new_permissions("userset", GroupFromLdapSerializer.PERMS_MAP["SETUP_USERSET"])

        # to_new_permissions("tagclass", GroupFromLdapSerializer.PERMS_MAP["GOODSCLASS_PERMS"])
        # to_new_permissions("goodsmodel", GroupFromLdapSerializer.PERMS_MAP["GOODSMODEL_PERMS"])
        # to_new_permissions("putaway", GroupFromLdapSerializer.PERMS_MAP["PUTAWAY_PERMS"])
        # to_new_permissions("singlegoods", GroupFromLdapSerializer.PERMS_MAP["SINGLE_GOODS_PERMS"])
        # to_new_permissions("multiplegoods", GroupFromLdapSerializer.PERMS_MAP["MULTIPLEGOODS_PERMS"])
        # to_new_permissions("advertising", GroupFromLdapSerializer.PERMS_MAP["ADVERTISING_PERMS"])
        # to_new_permissions("orderinfo", GroupFromLdapSerializer.PERMS_MAP["ORDER_INFO_PERMS"])
        to_new_permissions("data-overview", GroupFromLdapSerializer.PERMS_MAP["DATA_OVERVIEW"])
        to_new_permissions("support", GroupFromLdapSerializer.PERMS_MAP["SUPPORT"])
        instance.permissions.set(objs=Permission.objects.filter(codename__in=new_permissions))

    # 重写post请求的方法
    def create(self, validated_data):
        # 新建group,无permissions信息
        group = Group()
        group.name = validated_data['name']
        group.save()

        # 根据发送请求的格式为self.context['request'].content_type ："application/json"，即json式请求，取permission_dict
        permission_dict = self.initial_data['permissions']

        self.set_permissions(instance=group, validated_data=permission_dict)
        return group

    # 重写put请求的方法
    def update(self, instance, validated_data):
        super(GroupFromLdapSerializer, self).update(instance, validated_data)
        permission_dict = self.initial_data['permissions']

        # login_model = LoginLdapConfig.objects.all().values_list('login_model', flat=True)
        if login_model ==3 or login_model ==4:
            del_instance = instance.user_set.all()
        else:
            del_instance = instance.user_set.all().filter(user_profile__create_source=login_model)

        for item in del_instance:
            instance.user_set.remove(item)
        for each in self.initial_data['own_user']:
            user_id = each['id']
            user_instance = User.objects.all().get(pk=user_id)
            instance.user_set.add(user_instance)
            instance.save()

        self.set_permissions(instance=instance, validated_data=permission_dict)
        return instance


class UserFromLdapSerializer(serializers.ModelSerializer):
    groups = GroupForUserSerializer(many=True)

    def get_department(self, instance):
        ret = ''
        try:
            employee = instance.employee
            department = employee.department
            ret = department.dpt_name

        except Exception as e:
            raise TypeError(e)
        finally:
            return ret

    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'groups', 'department')

    # 重写put请求的方法
    def update(self, instance, validated_data):
        # 忽略groups信息，update本user,
        del validated_data['groups']
        super(UserFromLdapSerializer, self).update(instance, validated_data)

        #  self.context['request'].content_type == "application/json":  # json式请求
        group_list = self.initial_data['grop_list'].split(',')
        dpt_name = self.initial_data['department']

        # 清空本user中的groups信息，插入新的groups
        instance.groups.clear()
        for item in group_list:
            item = item.strip()
            instance.groups.add(Group.objects.get(name=item))

        department = Structure.objects.all().filter(dpt_name=dpt_name).first()
        if not department:
            raise Structure.DoesNotExist('%s部门信息填写错误' % dpt_name)

        employee = Employee.objects.filter(user=instance)
        if not employee.exists():
            Employee.objects.create(user=instance)
        instance.employee.department = department
        instance.employee.save()
        instance.save()
        return instance


class StructureSerializer(serializers.ModelSerializer):
    def get_own_user(self, department):
        own_user = User.objects.filter(employee__department=department)
        user_list = []
        role = []  # 角色
        for item in own_user:
            try:
                role = item.groups.values()

            except Exception as e:
                log.error(e)

            finally:
                user_list.append({'id': item.id, 'user_name': item.last_name, 'group': role})

        return user_list

    own_user = serializers.SerializerMethodField()

    class Meta:
        model = Structure
        fields = ('id', 'dpt_name', 'parent', 'own_user')
