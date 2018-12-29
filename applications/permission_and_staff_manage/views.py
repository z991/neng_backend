from __future__ import unicode_literals

import logging

from django.contrib.auth.models import User, Group, Permission
from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from applications.setup.models import LoginLdapConfig
from applications.setup.permissions import GroupListPermission, UserPermission
from applications.log_manage.models import OperateLog
from applications.permission_and_staff_manage.models import Structure
from applications.permission_and_staff_manage.serializers import GroupFromLdapSerializer, PermissionSerializer, \
    StructureSerializer, UserFromLdapSerializer, SimpGroupFromLdapSerializer
from libs.login_set import get_login_model
from ldap_server.ldap_config import login_model

log = logging.getLogger("Django")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related("employee__department").order_by('-id')
    serializer_class = UserFromLdapSerializer
    permission_classes = [UserPermission]

    def get_queryset(self):
        # 人员列表的search
        group_name = self.request.GET.get('group_name', "").strip()
        user_name = self.request.GET.get('username', "").strip()  # 人员
        dpt_name = self.request.GET.get('department', "").strip()  # 部门
        mode = login_model
        mode_dict = {1: 1, 2: 2, 3: 2, 4: 1}
        queryset = User.objects.all().filter(user_profile__create_source=mode_dict[mode]).select_related(
                "employee__department").order_by('-id')

        if dpt_name:
            queryset = queryset.filter(employee__department__dpt_name=dpt_name)
        if group_name:
            queryset = queryset.filter(groups__name__icontains=group_name)
        if user_name:
            queryset = queryset.filter(last_name__icontains=user_name)
        return queryset

    @detail_route(methods=['get'])
    def get_user_perm(self, request, pk=None):
        """

        """
        perm_dict = {
            'auth': {
                'view': 0,
                'group': {"view": 0},
                'user': {"view": 0},
                'structure': {"view": 0}
            },
            "ops": {
                'view': 0,
                "ref-server": {"view": 0},
                "server": {"view": 0},
                "ser-grp": {"view": 0},
                "grid": {"view": 0}
            },
            'pro': {
                'view': 0,
                "ref-product": {"view": 0},
                "product": {"view": 0}
            },
            'workorder_manage': {
                'view': 0,
                'openstationmanage': {"view": 0},
                'customer-khk': {"view": 0}
            },
            'log': {
                'view': 0,
                'system-log': {'view': 0},
                'personal-log': {'view': 0}
            },
            "data_manage": {
                "view": 0,
                "company-inquire": {"view": 0},
                "channel-inquire": {"view": 0},
                "grid-inquire": {"view": 0},
                "site-industry": {"view": 0},
            },
            'setup': {
                'view': 0,
                'help_center': {'view': 0},
                'industry': {'view': 0},
                'loginconfig': {'view': 0},
                # 'userset': {'view': 0}
            },
            # 'goods_manage': {
            #     'view': 0,
            #     'singlegoods': {'view': 0},
            #     'tagclass': {'view': 0},
            #     'goodsmodel': {'view': 0},
            #     'putaway': {'view': 0},
            #     'multiplegoods': {'view': 0},
            #     'advertising': {'view': 0}
            #     },
            'order_info_manage': {
                'view': 0,
                'orderinfo': {'view': 0}
            },
            'data_overview': {
                'view': 0,
                'data-overview': {'view': 0}
            },
            'version_manage': {
                "view": 0,
                "repository": {'view': 0}
            },
            'operatingtools':{
                "view": 0,
                "support": {"view": 0},
                "script-execution": {"view": 0}
            }

        }
        permissions = request.user.get_group_permissions()
        for item in permissions:
            app = item.split('.')[0]
            action, mod = item.split('.')[1].split('_')

            if action == 'view':
                # 角色权限模块
                if app == 'auth' and mod != 'permission':
                    perm_dict['auth']['view'] = 1
                    perm_dict['auth'][mod]['view'] = 1

                elif app == 'permission_and_staff_manage':
                    if mod != 'employee':
                        perm_dict['auth']['view'] = 1
                        perm_dict['auth'][mod]['view'] = 1

                # 产品管理模块权限和运维管理模块权限
                elif app == 'production_manage':
                    if mod in ['grid', 'servergroup', 'server']:
                        perm_dict['ops']['view'] = 1  # 运维配置
                        if mod == 'grid':
                            perm_dict['ops']['grid']['view'] = 1
                        elif mod == 'servergroup':
                            perm_dict['ops']['ser-grp']['view'] = 1

                        elif mod == 'server':
                            perm_dict['ops']['server']['view'] = 1
                            perm_dict['ops']['ref-server']['view'] = 1

                    elif mod in ['versioninfo', 'product', 'singleselection', 'functioninfo']:
                        perm_dict['pro']['view'] = 1  # 产品配置
                        perm_dict['pro']['ref-product']['view'] = 1  # 产品配置--重构版产品
                        perm_dict['pro']['product']['view'] = 1  # 产品配置--经典版产品

                # 工单管理
                elif app == 'workorder_manage':
                    perm_dict['workorder_manage']['view'] = 1
                    if mod == 'openstationmanage':
                        perm_dict['workorder_manage'][mod]['view'] = 1  # 开站
                    elif mod == 'industry':
                        perm_dict['setup'][mod]['view'] = 1
                    elif mod == 'customer-khk':
                        perm_dict["workorder_manage"][mod]['view'] = 1  # 客户库

                # 日志
                elif app == 'log_manage':
                    perm_dict['log']['view'] = 1
                    if mod == 'system-log':
                        perm_dict['log'][mod]['view'] = 1
                    elif mod == 'personal-log':
                        perm_dict['log'][mod]['view'] = 1

                # 数据管理
                elif app == 'data_manage':
                    perm_dict['data_manage']['view'] = 1
                    if mod == 'company-inquire':
                        perm_dict['data_manage'][mod]['view'] = 1
                    if mod == 'channel-inquire':
                        perm_dict['data_manage'][mod]['view'] = 1
                    if mod == 'grid-inquire':
                        perm_dict['data_manage'][mod]['view'] = 1
                    if mod == 'site-industry':
                        perm_dict['data_manage'][mod]['view'] = 1
                # 设置
                elif app == 'setup':
                    perm_dict['setup']['view'] = 1
                    if mod == 'sitereceptiongroup':
                        perm_dict['setup']['help_center']['view'] = 1

                    elif mod == 'loginconfig':
                        perm_dict['setup']['loginconfig']['view'] = 1

                    # elif mod == 'userset':
                    #     perm_dict['setup']['userset']['view'] = 1

                # 商品管理模块权限
                # elif app == 'goods':
                #     perm_dict['goods_manage']['view'] = 1
                #     if mod == 'tagclass':
                #         perm_dict['goods_manage']['tagclass']['view'] = 1
                #
                #     elif mod == 'goodsmodel':
                #         perm_dict['goods_manage']['goodsmodel']['view'] = 1
                #
                #     elif mod == 'putaway':
                #         perm_dict['goods_manage']['putaway']['view'] = 1
                #
                #     elif mod == 'singlegoods':
                #         perm_dict['goods_manage']['singlegoods']['view'] = 1
                #
                #     elif mod == 'advertising':
                #         perm_dict['goods_manage']['advertising']['view'] = 1
                #
                #     elif mod == 'multiplegoods':
                #         perm_dict['goods_manage']['multiplegoods']['view'] = 1

                # # 订单管理模块权限
                # elif app == 'order_manage':
                #     perm_dict['order_info_manage']['view'] = 1
                #     if mod == 'orderinfo':
                #         perm_dict['order_info_manage']['orderinfo']['view'] = 1

                # 数据总览模块(首页)
                # 首页
                elif app == 'data_overview':
                    perm_dict['data_overview']['view'] = 1
                    if mod == 'data-overview':
                        perm_dict['data_overview']["data-overview"]['view'] = 1
                # 版本管理模块
                elif app == 'version_manage':
                    perm_dict['version_manage']['view'] = 1
                    if mod == "versionrepository":
                        perm_dict["version_manage"]["repository"]['view'] = 1
                # 运营工具
                elif app == "operatingtools":
                    perm_dict["operatingtools"]["view"] =1
                    if mod == "support":
                        perm_dict[app][mod]["view"] = 1
                    if mod == "script-execution":
                        perm_dict[app][mod]["view"] = 1
            perm_dict.update({'user_name': request.user.last_name})
        return JsonResponse(perm_dict)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(UserViewSet, self).update(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        super(UserViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        super(UserViewSet, self).destroy(request, *args, **kwargs)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('-id')
    permission_classes = [GroupListPermission]

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return SimpGroupFromLdapSerializer
        else:
            return GroupFromLdapSerializer

    def get_queryset(self):
        # 通过改写queryset ,实现搜索角色和查看人员的角色列表
        queryset = Group.objects.all().order_by('-id')
        group_name = self.request.GET.get('group_name', "").strip()
        if group_name:  # 实现搜索角色
            queryset = queryset.filter(name__icontains=group_name)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        group_instance = serializer.data
        return Response(group_instance)

    def create(self, request, *args, **kwargs):
        # 角色新增
        group_data = request.data
        group_serializer = self.get_serializer(data=group_data)

        try:
            group_serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            instance = group_serializer.create(group_data)
        OperateLog.create_log(request)
        return Response(GroupFromLdapSerializer(instance).data, status=status.HTTP_200_OK)

    @staticmethod
    def get_user_dict(request) -> dict:
        role_id = request.GET.get('role_id', '').strip()
        # login_model = LoginLdapConfig.objects.all().values_list('login_model', flat=True)
        if login_model == 3 or login_model == 4:
            all_user_query = User.objects.all()
            this_user = Group.objects.all().get(pk=role_id).user_set.all()\
                .values_list("id", "last_name", "user_profile__create_source")
        else:
            all_user_query = User.objects.all().filter(user_profile__create_source=login_model)

            this_user = Group.objects.all().get(pk=role_id).user_set.all()\
                .filter(user_profile__create_source=login_model)\
                .values_list("id", "last_name", "user_profile__create_source")

        all_user = all_user_query.values_list('id', 'last_name', 'user_profile__create_source')

        all_user_list = []
        this_user_list = []
        for each in all_user:
            all_user_list.append(dict(zip(['id', 'last_name', 'source'], each)))

        for item in this_user:
            this_user_list.append(dict(zip(['id', 'last_name', 'source'], item)))
        result = {'all_user': all_user_list, 'this_user': this_user_list}
        return result

    @list_route(methods=['get'])
    def get_user(self, request):
        result = self.get_user_dict(self.request)
        list_all_id = []
        list_this_id = []
        for each in result['all_user']:
            list_all_id.append(each['id'])
        for item in result['this_user']:
            list_this_id.append(item['id'])
        left_list = []
        right_list = result['this_user']
        list_this_id = list(set(list_all_id).difference(set(list_this_id)))

        for eag in result['all_user']:
            if eag['id'] in list_this_id:
                left_list.append(eag)

        return Response(status=status.HTTP_200_OK, data={'left_list': left_list, 'right_list': right_list})

    def update(self, request, *args, **kwargs):
        # 角色修改
        try:
            with transaction.atomic():
                super(GroupViewSet, self).update(request, *args, **kwargs)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(GroupViewSet, self).destroy(request, *args, **kwargs)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class StructureViewSet(viewsets.ModelViewSet):
    queryset = Structure.objects.all().order_by('-id')
    serializer_class = StructureSerializer

    @list_route(methods=['get'])
    def get_structure_tree(self, request):
        # 获取组织架构树
        temp_list = []
        ret = {}
        try:
            dept0 = Structure.objects.all().filter(parent__isnull=True).first()  # 根级
            dept1_list = Structure.objects.all().filter(parent=dept0)  # 一级
            i = 0
            for item in dept1_list:
                dept2_temp = Structure.objects.all().filter(parent=item)  # 二级
                data_temp = []
                if dept2_temp.exists() == 0:
                    temp_list.append({'id': item.id, 'name': item.dpt_name, 'children': data_temp})
                    continue

                for section in dept2_temp:
                    section = StructureSerializer(section)
                    data_temp.append({'id': section.data['id'], 'name': section.data['dpt_name']})

                temp_list.append({'id': item.id, 'name': item.dpt_name, 'children': data_temp})
                i += 1
            ret['id'] = dept0.id
            ret['name'] = dept0.dpt_name
            ret['children'] = temp_list
            return JsonResponse(ret)
        except Exception as e:
            log.error(e)
            return JsonResponse('', safe=False)
