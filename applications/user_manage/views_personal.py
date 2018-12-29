import logging
import ast

from passlib.hash import ldap_salted_sha1 as sha
from ldap3 import MODIFY_REPLACE, SUBTREE
from .common import connect_ldap
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from applications.log_manage.models import OperateLog
from libs.login_set import get_login_model
from ldap_server.ldap_config import login_model

log = logging.getLogger('django')


@csrf_exempt
def personal_changepassword(request):
    if not request.method == "POST":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    data = ast.literal_eval(request.body.decode('utf-8'))
    user = request.user.get_username()

    OperateLog.create_log(request)

    mode = login_model
    # 校验ldap是否有该用户
    ldap_exit = User.objects.filter(user_profile__create_source=1).filter(username=user).exists()
    # 校验本地是否有该用户
    local_exit = User.objects.filter(user_profile__create_source=2).filter(username=user).exists()

    # ldap
    if mode == 1:
        ldap_change_password(request, **data)
        user = User.objects.filter(user_profile__create_source=1).get(username=user)
        user.password = sha.hash(data["new_password"])
        user.save()
    # 本地
    elif mode == 2:
        user = User.objects.filter(user_profile__create_source=2).get(username=user)
        if sha.verify(data['old_password'], user.password):
            user.password = sha.hash(data["new_password"])
            user.save()
    # 本地+ldap   ldap+本地
    elif mode == 3 or mode == 4:
        if ldap_exit:
            ldap_change_password(request, **data)
            user = User.objects.filter(user_profile__create_source=1).get(username=user)
            user.password = sha.hash(data["new_password"])
            user.save()
        if local_exit:
            user = User.objects.filter(user_profile__create_source=2).get(username=user)
            if sha.verify(data['old_password'], user.password):
                user.password = sha.hash(data["new_password"])
                user.save()
    return JsonResponse(status=status.HTTP_200_OK, data={"info": "修改成功"})


def ldap_change_password(request, **data):
    try:
        with connect_ldap() as c:
            c.search(get_login_model().user_ldapsearch,
                     search_filter='(objectClass=inetOrgPerson)',
                     attributes=['userPassword', 'cn'],
                     search_scope=SUBTREE)
            ldap_password = ''
            dn = ''
            for i in c.entries:
                if i.entry_attributes_as_dict['cn'][0] == request.user.get_username():
                    ldap_password = i.entry_attributes_as_dict['userPassword'][0]
                    dn = i.entry_dn
                    break
            if ldap_password and sha.verify(data['old_password'], ldap_password):
                c.modify(dn, {'userpassword': [(MODIFY_REPLACE, sha.hash(data['new_password']))]})
    except Exception as e:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST,
                            data={"error": "ldap密码修改失败", "e": str(e.args)})
