import re
import logging
import json

from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from applications.user_manage.base_views import member_clear
from ldap3 import MODIFY_REPLACE
from django.views.decorators.csrf import csrf_exempt
from .common import connect_ldap
from rest_framework.response import Response
from rest_framework import status
from passlib.hash import ldap_salted_sha1 as sha
from rest_framework.decorators import api_view
from applications.log_manage.models import OperateLog

from libs.login_set import get_login_model
from applications.setup.models import UserProfile
from applications.user_manage.base_views import get_oa_group
from applications.user_manage.models import LdapUser
from ldap_server.ldap_config import login_model

log = logging.getLogger('django')


# 用户列表
@api_view(['GET'])
# @permission_classes([SystemUserPermission, ])
def user_list(request):
    OperateLog.create_log(request)
    # 前端传过来的页码
    page = request.GET.get('page', 1)
    page = int(page)

    if page == 1:
        start = 0
        end = 10
    else:
        start = 10 * (page - 1)
        end = 10 * page

    # 获取登录模式
    login_sets = get_login_model()
    mode = login_model
    # 1 ldap 2.本地  3.本地+ldap  4.ldap+本地
    # 获取ldap，本地+ldap的用户
    if mode == 1:
        user_l = User.objects.exclude(user_profile__create_source=2).values('username', 'last_name')
    # 获取本地，本地+ldap的用户
    elif mode == 2:
        user_l = User.objects.exclude(user_profile__create_source=1).values('username', 'last_name')
    # 获取所有用户
    elif mode == 3 or mode == 4:
        user_l = User.objects.distinct().values('username', 'last_name')

    result = []
    u_result = []
    # 获取用户总页数
    count = user_l.count()
    total_page = (count // 10) + 1

    for u in user_l:
        if u not in result:
            result.append(u)

    total_result = result

    OperateLog.create_log(request)
    result = result[start:end]

    return Response({"total_count": count, "total_page": total_page,
                     "result": result, "total_result": total_result}, status=status.HTTP_200_OK)


# 用户详情
@api_view(['GET'])
def user_detail(request):
    user = request.GET.get("user", "")
    oa_group = get_oa_group()

    permission = []
    try:
        login_sets = get_login_model()
        mode = login_model
        # 1 ldap 2.本地  3.本地+ldap  4.ldap+本地
        # 获取ldap，本地+ldap的用户

        # 校验ldap是否有该用户
        ldap_exit = User.objects.filter(user_profile__create_source=1).filter(username=user).exists()
        # 校验本地是否有该用户
        local_exit = User.objects.filter(user_profile__create_source=2).filter(username=user).exists()

        # 获取用户所有信息
        if mode == 1:
            user_single = User.objects.filter(user_profile__create_source=1).get(username=user)
        elif mode == 2:
            user_single = User.objects.filter(user_profile__create_source=2).get(username=user)
        elif mode == 3:
            if local_exit:
                user_single = User.objects.filter(user_profile__create_source=2).get(username=user)
            else:
                user_single = User.objects.filter(user_profile__create_source=1).get(username=user)
        elif mode == 4:
            if ldap_exit:
                user_single = User.objects.filter(user_profile__create_source=1).get(username=user)
            else:
                user_single = User.objects.filter(user_profile__create_source=2).get(username=user)

        u_id = user_single.id


        # 获取该用户所有的分组
        gr = Group.objects.filter(user__id=u_id).values('id', 'name')

        cn = user_single.username
        sn = user_single.last_name
        mail = user_single.email
        s_dict = {1: "ldap", 2: "本地"}
        create_source = user_single.user_profile.create_source

        # 遍历系统所有分组
        for oa in oa_group:
            # 遍历用户的所有分组
            for g in gr:
                if oa["id"] == g["id"]:
                    oa["view"] = 1
            permission.append(oa)
        data = {"cn": cn,
                "sn": sn,
                "mail": mail,
                "create_source": s_dict[create_source],
                "permission": permission}

        return JsonResponse({"data": data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


# 用户新增
@csrf_exempt
def user_add(request):
    OperateLog.create_log(request)
    if not request.method == "POST":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})

    # 当前用户是否拥有新增用户权限
    permission = request.user.has_perm("auth.add_user")
    if permission == False:
        return JsonResponse({"error": "你没有权限操作"}, status=status.HTTP_403_FORBIDDEN)
    bod = request.body
    bod = str(bod, encoding="utf-8")
    data = json.loads(bod)

    username = data["cn"]
    # 校验ldap是否有该用户
    ldap_exit = User.objects.filter(user_profile__create_source=1).filter(username=username).exists()
    # 校验本地是否有该用户
    local_exit = User.objects.filter(user_profile__create_source=2).filter(username=username).exists()

    # 获取登录模式
    login_sets = get_login_model()
    mode = login_model

    if mode == 1:
        # 如果ldap没有该用户
        if ldap_exit == False:
            with transaction.atomic():
                ldap_user_add(**data)
                lu = local_user_add(**data)
                up = UserProfile.objects.create(user=lu, create_source=1, is_enable=1)
            return JsonResponse({"info": "新增成功"}, status=status.HTTP_200_OK)

        # 如果ldap存在该用户
        else:
            return JsonResponse({"error": "ldap已存在该用户"}, status=status.HTTP_400_BAD_REQUEST)

    elif mode == 2:
        # 如果本地没有该用户
        if local_exit == False:
            with transaction.atomic():
                lu = local_user_add(**data)
                up = UserProfile.objects.create(user=lu, create_source=2, is_enable=1)
            return JsonResponse({"info": "新增成功"}, status=status.HTTP_200_OK)
        # 如果本地存在该用户
        else:
            return JsonResponse({"error": "本地已存在该用户"}, status=status.HTTP_400_BAD_REQUEST)
    elif mode == 3 or mode == 4:
        # 本地或者ldap存在该用户则不进行新增
        if (ldap_exit == False) and (local_exit == False):
            with transaction.atomic():
                # ldap新增
                ldap_user_add(**data)
                lu = local_user_add(**data)
                lup = UserProfile.objects.create(user=lu, create_source=1, is_enable=1)
                # 本地新增
                bu = local_user_add(**data)
                bup = UserProfile.objects.create(user=bu, create_source=2, is_enable=1)
            return JsonResponse({"info": "新增成功"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": "ldap或本地已存在该用户"}, status=status.HTTP_400_BAD_REQUEST)


# ldap用户新增
def ldap_user_add(**data):
    cn = data['cn']
    try:
        with connect_ldap() as c:
            login_sets = get_login_model()
            user_search = login_sets.user_ldapsearch
            base_cn = 'cn=%s' % cn
            base_dn = base_cn+','+user_search
            c.add(base_dn,
                  ['inetOrgPerson', 'top', 'ldapPublicKey'],
                  {'sn': data['sn'],
                   'mail': '%s@xiaoneng.cn' % data['cn'],
                   "userpassword": sha.hash(data['password']),
                   "sshPublicKey": data.get('sshPublicKey', ''),}
                  )
    except Exception as e:
        return str(e.args)


# 本地用户新增
def local_user_add(**data):
    user_info = {"username": data["cn"],
                 "password": sha.hash(data["password"]),
                 "email": '%s@xiaoneng.cn' % data['cn'],
                 "last_name": data["sn"]}
    # permission：[{'id': 16, 'name': '管理员', 'view': 1},
             # {'id': 23, 'name': '行政', 'view': 0},
             # {'id': 22, 'name': '运维', 'view': 1}]
    user = User.objects.create(**user_info)
    permisson = data["permission"]
    for per in permisson:
        if per["view"] == 1:

            # 将用户添加分组
            group = Group.objects.get(pk=per["id"])
            user.groups.add(group)
    return user


# ldap用户信息修改
def ldap_user_put(**data):
    try:
        with connect_ldap() as c:
            login_sets = get_login_model()
            user_search = login_sets.user_ldapsearch
            base_cn = 'cn=%s' % data['cn']
            dn = base_cn + ',' + user_search
            modify_sn = (MODIFY_REPLACE, data['sn'])
            modify_mail = (MODIFY_REPLACE, data['mail'])

            c.modify(dn, {'sn': [modify_sn]})
            c.modify(dn, {'mail': [modify_mail]})
    except Exception as e:
        return str(e.args)


# 本地用户修改
def local_user_put(**data):
    #data {"id":1, "cn":"zhuxuanyu", "sn":"帅", "permission":[]}
    username = data["cn"]
    last_name = data["sn"]
    eamil = data["mail"]
    permission = data["permission"]
    idu = User.objects.filter(user_profile__is_enable=1).filter(username=username)
    for i in idu:
        user = User.objects.get(pk=i.id)
        user.last_name = last_name
        user.email = eamil
        # 对用户组操作
        user.groups.clear()
        for g in permission:
            # 将用户添加分组
            if g["view"] == 1:
                group = Group.objects.get(pk=g["id"])
                user.groups.add(group)
        user.save()


# 用户修改
@csrf_exempt
def user_put(request):
    """
    :param request: sn, permission_list,cn
    :return: None
    """
    OperateLog.create_log(request)
    if not request.method == "PUT":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    permission = request.user.has_perm("auth.change_user")
    if permission == False:
        return JsonResponse({"error": "你没有权限操作"}, status=status.HTTP_403_FORBIDDEN)

    bod = request.body
    bod = str(bod, encoding="utf-8")
    data = json.loads(bod)

    username = request.user.username

    # 获取登录模式
    login_sets = get_login_model()
    mode = login_model

    # 校验ldap是否有该用户
    ldap_exit = User.objects.filter(user_profile__create_source=1).filter(username=username).exists()
    # 校验本地是否有该用户
    local_exit = User.objects.filter(user_profile__create_source=2).filter(username=username).exists()

    try:
        if mode == 1:
            with transaction.atomic():
                ldap_user_put(**data)
                local_user_put(**data)
        elif mode == 2:
            with transaction.atomic():
                local_user_put(**data)
        elif mode == 3 or mode == 4:
            if ldap_exit:
                ldap_user_put(**data)
                local_user_put(**data)
            if local_exit:
                local_user_put(**data)
        return JsonResponse({"info": "修改成功"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "修改失败", "message": str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


# ldap删除
def ldap_user_delete(cn):
    cn = cn
    login_sets = get_login_model()
    user_search = login_sets.user_ldapsearch
    base_cn = 'cn=%s' % cn
    dn = base_cn + ',' + user_search

    try:
        with connect_ldap() as c:
            # 清除用户所有角色后删除
            member_clear(cn)
            c.delete(dn)
    except Exception as e:
        return JsonResponse({"error": "删除失败: " + str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


# 用户删除
@csrf_exempt
def user_delete(request):
    OperateLog.create_log(request)
    if not request.method == "DELETE":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    permission = request.user.has_perm("auth.delete_user")
    if permission == False:
        return JsonResponse({"error": "你没有权限操作"}, status=status.HTTP_403_FORBIDDEN)
    cn = request.GET.get('cn', '')
    # 获取登录模式
    login_sets = get_login_model()
    mode = login_model
    try:
        if mode == 1:
            # 删除ldap用户信息
            ldap_user_delete(cn)
            ret = User.objects.filter(user_profile__create_source=1).filter(username=cn).delete()
        elif mode == 2:
            ret = User.objects.filter(user_profile__create_source=2).filter(username=cn).delete()
        elif mode == 3 or mode == 4:
            # 删除ldap用户信息
            ldap_user_delete(cn)
            ret = User.objects.filter(username=cn).delete()
        return JsonResponse({"message": "删除成功"}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": "删除失败: " + str(e.args)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_groups(request):
    groups = get_oa_group()
    return Response(data=groups, status=status.HTTP_200_OK)


@api_view(['GET'])
def ldap_local(request):
    permission = request.user.has_perm("setup.view_userset")
    if permission == False:
        return JsonResponse({"error": "你没有权限操作"}, status=status.HTTP_403_FORBIDDEN)

    ldap_user = LdapUser.objects.all()
    gr_xiaoneng = Group.objects.get(name="小能人")

    for ld in ldap_user:
        exits = User.objects.filter(user_profile__create_source=1).filter(username=ld.username).exists()
        if exits == False:
            defaults = {
                "username": ld.username,
                "last_name": ld.user_sn,
                "email": ld.email,
                "password": ld.password
            }
            user = User.objects.create(**defaults)

            up = UserProfile.objects.create(user=user, create_source=1, is_enable=1)
            user.groups.add(gr_xiaoneng)
    return Response(data='同步成功', status=status.HTTP_200_OK)