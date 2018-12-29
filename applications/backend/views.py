import logging
import datetime
import requests
import json
from passlib.hash import ldap_salted_sha1 as sha

from django.contrib import auth
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

from applications.backend.models import LdapUser
from applications.backend.serializers import Userserializer
from applications.log_manage.models import OperateLog
from applications.setup.models import LoginLdapConfig
from libs.login_set import get_login_model
log = logging.getLogger('django')
# from ldap_server.settings import AUTHENTICATION_BACKENDS

@csrf_exempt
def login(request):
    """
        author:zxy
        function:登录验证
        param :request 前端发来的请求
        return: 以user.id为内容的JsonResponse
        """
    # 判断请求类型
    if not request.method == "POST":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    params = request.POST
    post_code = params.get("check_code", "").lower()
    session_code = request.session.get('verifycode', "").lower()
    username = params.get("username", "")
    # 输入的密码
    password = params.get("password", "")

    # 判断验证码
    if (not post_code) or (session_code != post_code):
        return JsonResponse({"error": "验证码错误"}, status=status.HTTP_417_EXPECTATION_FAILED, safe=False)

    # 1:ldap  2: 本地  3: 本地+ldap 4: ldap+本地
    login_mode = get_login_model()
    mode = login_mode.login_model

    try:
        use = User.objects.filter(username=username).first()
        if use and use.is_superuser == True:
            if use.password.startswith('{SSHA}'):
                ps = sha.verify(password, use.password)
            else:
                ps = check_password(password, use.password)
            if ps == False:
                return JsonResponse({"error": "密码错误"}, status=status.HTTP_400_BAD_REQUEST)
            auth.login(request, use)
    except:
        pass
    if not use or (use and use.is_superuser==False):
        # ldap验证
        if mode == 1:
            try:
                use = User.objects.filter(user_profile__create_source=1).get(username=username)
                password_t = use.password
                very = sha.verify(password, password_t)
                if very == False:
                    return JsonResponse({"error": "密码错误"}, status=status.HTTP_400_BAD_REQUEST)
                auth.login(request, use)
            except Exception as e:
                return JsonResponse({'error': '该用户不存在', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # 本地验证
        elif mode == 2:
            try:
                # daigaigg
                use = User.objects.filter(user_profile__create_source=2).get(username=username)
                password_t = use.password
                very = sha.verify(password, password_t)
                if very == False:
                    return JsonResponse({"error": "密码错误"}, status=status.HTTP_400_BAD_REQUEST)

                auth.login(request, use)
            except Exception as e:
                return JsonResponse({'error': '该用户不存在', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # 本地优先
        elif mode == 3:
            use = User.objects.filter(user_profile__create_source=2).filter(username=username).first()
            use1 = User.objects.filter(user_profile__create_source=1).filter(username=username).first()
            try:
                if use:
                    use = use
                elif use == None:
                    use = use1
                elif use1 == None:
                    return JsonResponse({"error": "该用户不存在"}, status=status.HTTP_400_BAD_REQUEST)
                password_b = use.password
                very = sha.verify(password, password_b)
                if very == False:
                    return JsonResponse({"error": "密码错误"}, status=status.HTTP_400_BAD_REQUEST)
                auth.login(request, use)
            except Exception as e:
                return JsonResponse({"error": "该用户不存在"}, status=status.HTTP_400_BAD_REQUEST)

        # ldap优先
        elif mode == 4:
            use = User.objects.filter(user_profile__create_source=1).filter(username=username).first()
            use1 = User.objects.filter(user_profile__create_source=2).filter(username=username).first()
            try:
                if use:
                    use = use
                elif use == None:
                    use = use1
                elif use1 == None:
                    return JsonResponse({"error": "该用户不存在"}, status=status.HTTP_400_BAD_REQUEST)
                password_b = use.password
                very = sha.verify(password, password_b)
                if very == False:
                    return JsonResponse({"error": "密码错误"}, status=status.HTTP_400_BAD_REQUEST)
                auth.login(request, use)
            except Exception as e:
                return JsonResponse({"error": "该用户不存在"}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"id": use.id}, status=status.HTTP_200_OK)


def logout(request):
    """
    function:登出
    param: request 
    return: 
    """
    if not request.method == "GET":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    if request.user.is_authenticated:
        OperateLog.logout(request)  # 登出日志
    auth.logout(request)
    return HttpResponse('success', status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    function:测试用
    """
    queryset = LdapUser.objects.all()
    serializer_class = Userserializer