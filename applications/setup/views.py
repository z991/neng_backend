# Create your views here.
import boto3
import json
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import permission_classes, api_view

from applications.log_manage.models import OperateLog
from applications.production_manage.models import DataBaseInfo
from applications.setup.models import SiteReceptionGroup
from applications.setup.permissions import SiteReceptionGroupPermission,\
    IndustryGroupPermission, LoginConfigPermission
from applications.setup.serializers import CliIndustrySerializer
from applications.setup.serializers import SiteReceptionGroupSerializer
from applications.workorder_manage.models import Industry
from libs.hash import decrypt, get_md5
from libs.login_set import get_login_model
from libs.image import image_resize
from libs.mysql_helper import Connection
from applications.setup.models import LoginLdapConfig, UserProfile
from django.contrib.auth.models import User
from ldap_server.ldap_config import login_model


class CliIndustrySet(viewsets.ModelViewSet):
    queryset = Industry.objects.all().order_by('-id').prefetch_related('company_info')
    serializer_class = CliIndustrySerializer
    permission_classes = [IndustryGroupPermission]

    def is_unique(self, industry):
        industry_list = Industry.objects.all().values_list('industry', flat=True)
        if industry in industry_list:
            return 0
        else:
            return 1

    def create(self, request, *args, **kwargs):
        industry = request.data.get('industry', '').strip()
        if industry:
            if self.is_unique(industry):
                Industry.objects.create(industry=industry)
                OperateLog.create_log(request)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({'error': '该行业已存在'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '参数错误，无行业名'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        industry = request.data.get('industry', '').strip()
        instance = self.get_object()

        if industry:
            if industry == instance.industry:
                return Response(status=status.HTTP_200_OK)
            elif self.is_unique(industry):
                instance.industry = industry
                instance.save()
                OperateLog.create_log(request)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'error': '该行业已存在'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '参数错误，无行业名'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        site_num = instance.company_info.count()
        if not site_num:
            instance.delete()
            OperateLog.create_log(request)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "有站点在该行业，不可删除"}, status=status.HTTP_400_BAD_REQUEST)


class SiteReceptionGroupView(ModelViewSet):
    """站点接待组接口的统一入口"""
    queryset = SiteReceptionGroup.objects.all().order_by('-id')
    serializer_class = SiteReceptionGroupSerializer
    permission_classes = [SiteReceptionGroupPermission]

    def get_queryset(self):
        queryset = SiteReceptionGroup.objects.all()
        title = self.request.GET.get("title", None)
        manager = self.request.GET.get("manager", None)
        company_id = self.request.GET.get("company_id", "").strip()
        if title:
            queryset = queryset.filter(title__icontains=title)
            # queryset = queryset.filter(group_id=title)
        if manager:
            queryset = queryset.filter(manager__icontains=manager)
        if company_id:
            queryset = queryset.filter(set_info__company_id=company_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.set_info.clear()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


@csrf_exempt
def reception_groups(request):
    """小能的客服组保存在bj-v4的t2d_syssetting表中，对应site_id为kf_8008
    从中获取到接待组的id和名称，返回给前端
    """
    db_info = DataBaseInfo.objects.get(grid__grid_name="bj-v4", db_name="kf")
    conn = Connection(database="kf", host=db_info.db_address, user=db_info.db_username,
                      password=decrypt(db_info.db_pwd), port=int(db_info.db_port))
    sql = "SELECT name, id FROM t2d_syssetting WHERE siteid='kf_8008'"
    reception_groups = conn.query(sql)
    conn.close()
    return JsonResponse(reception_groups, safe=False)


@csrf_exempt
def avatar_upload(request):
    """头像上传接口，上传jpeg图片，返回该图片的url"""
    if not request.method == "POST":
        return JsonResponse({"error": "request method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    cli = boto3.client(**settings.BAISHANYUN_CONFIGS)  # 获得客户端会话对象

    file = request.FILES['file']
    assert isinstance(file, UploadedFile)  # 获取到的文件信息应为一个UploadedFile对象

    file_type = file.name.split(".")[-1]
    if file_type not in ("jpg", "jpeg", "png"):
        return JsonResponse({"error": "文件格式不合法，目前只支持jpeg, jpg, png"}, status=status.HTTP_400_BAD_REQUEST)
    # 图片压缩，统一为280 * 280, jpeg格式
    # data = image_resize(
    #     data=file.read(),
    #     size=settings.AVATAR_SIZE,
    # )
    data = file.read()
    key = get_md5(data)
    cli.put_object(
        ACL='public-read',  # 公共可读
        Bucket='minioss',  # 固定
        Key=f"oa/{key}.jpeg",  # 文件保存在oa目录下
        ContentType=f'image/jpeg',
        Body=data
    )
    url = f'http://s2.i.qingcdn.com/minioss/oa/{key}.jpeg'
    return HttpResponse(url)

#http://kfoa.ntalker.com/index.php?m=Admin&c=Group&a=index&userid=###USERID###&siteid=###SITEID###&token=###TOKEN###
#http://oa-server.ntalker.com/public/help_center?siteid=###SITEID###&userid=###USERID###
def help_center(request):
    if not request.method == "GET":
        return JsonResponse({"error": "request method not allowed"})
    site_id = request.GET.get("siteid", "")
    user_id = request.GET.get("userid", "")
    user_id = "_".join(user_id.split("_ISME9754_T2D_"))
    site_reception_obj = SiteReceptionGroup.objects.filter(set_info__company_id=site_id).first()
    if not site_reception_obj:
        return JsonResponse({"error": "Invalid site_id"}, status=status.HTTP_400_BAD_REQUEST)
    data = {
        "company_name": "",
        "site_id": site_id,
        "reception_group_id": site_reception_obj.group_id,
        "user_id": user_id,
        "avatar": site_reception_obj.avatar,
        "manager": site_reception_obj.manager,
        "phone_number": site_reception_obj.phone_number,
        "email": site_reception_obj.email,
        "url": site_reception_obj.url,
        "desc": site_reception_obj.desc,
    }
    return render(request, "help_center.html", data)


@csrf_exempt
def login_config(request):
    if not (request.method == "PUT" or request.method == "POST"):
        return JsonResponse({"error": "request method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    permission = request.user.has_perm("setup.change_loginconfig")
    if permission == False:
        return JsonResponse({"error": "你没有权限操作"}, status=status.HTTP_403_FORBIDDEN)
    bod = request.body
    bod = str(bod, encoding="utf-8")
    bod = json.loads(bod)

    # 获取参数
    auth_ldap_bind_dn = bod.get("AUTH_LDAP_BIND_DN", "cn=admin,dc=xiaoneng,dc=cn")
    auth_ldap_bind_password = bod.get("AUTH_LDAP_BIND_PASSWORD", "password6666")
    user_ldapsearch = bod.get("USER_LDAPSearch", "ou=Users,dc=xiaoneng,dc=cn")
    user_scope_subtree = bod.get("USER_SCOPE_SUBTREE", "(cn=%(user)s)")
    group_ldapsearch = bod.get("GROUP_LDAPSearch", "cn=LDAP,ou=Roles,dc=xiaoneng,dc=cn")
    group_scope_subtree = bod.get("GROUP_SCOPE_SUBTREE", "(objectClass=groupOfUniqueNames)")
    is_active = bod.get("is_active", "(objectClass=groupOfUniqueNames)")
    is_staff = bod.get("is_staff", "cn=users,cn=LDAP,ou=Roles,dc=xiaoneng,dc=cn")
    is_superuser = bod.get("is_superuser", "cn=ldap-admin,cn=LDAP,ou=Roles,dc=xiaoneng,dc=cn")
    ldap_server_url = bod.get("ldap_server_url", "ldap.xiaoneng.cn")
    ldap_name = bod.get("ldap_name", "ldap://ldap.xiaoneng.cn")
    login_model = bod.get("login_model")

    model_info = {
        "auth_ldap_bind_dn": auth_ldap_bind_dn,
        "auth_ldap_bind_password": auth_ldap_bind_password,
        "user_ldapsearch": user_ldapsearch,
        "user_scope_subtree": user_scope_subtree,
        "group_ldapsearch": group_ldapsearch,
        "group_scope_subtree": group_scope_subtree,
        "is_active": is_active,
        "is_staff": is_staff,
        "is_superuser": is_superuser,
        "ldap_server_url": ldap_server_url,
        "ldap_name": ldap_name,
        "login_model": login_model,
        "ldap": "oa"
    }
    ret = LoginLdapConfig.objects.update_or_create(defaults=model_info, **{"ldap": "oa"})
    if login_model == '1':
        pro1 = UserProfile.objects.filter(create_source=1).update(is_enable=1)
        pro2 = UserProfile.objects.filter(create_source=2).update(is_enable=0)
    elif login_model == '2':
        pro1 = UserProfile.objects.filter(create_source=1).update(is_enable=0)
        pro2 = UserProfile.objects.filter(create_source=2).update(is_enable=1)
    elif login_model == '3' or login_model == '4':
        pro = UserProfile.objects.update(is_enable=1)
    OperateLog.create_log(request)
    return JsonResponse({'info': '设置成功'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def login_models(request):
    """
    当前登录模式
    :param request:
    :return:
    """
    mode_dict = {1: "ldap登录模式", 2: "本地验证模式", 3: "本地+ldap", 4: "ldap和本地验证"}
    login_mode = LoginLdapConfig.objects.get(ldap="oa").login_model
    model = mode_dict.get(login_mode)
    return JsonResponse({"login_model": model}, status=status.HTTP_200_OK)


@api_view(['GET'])
def sync_user(request):
    user_all = User.objects.all()
    user_list = []
    for u in user_all:
        exits = UserProfile.objects.filter(user=u).exists()
        user_info = {
            "user": u,
            "create_source": 1,
            "is_enable": 1
        }
        if exits == False:
            user_list.append(UserProfile(**user_info))
    ret = UserProfile.objects.bulk_create(user_list)
    return JsonResponse({"info": "创建成功"}, status=status.HTTP_200_OK)


@csrf_exempt
def save_accessory(request):
    """上传附件，返回该附件的url"""
    if not request.method == "POST":
        return JsonResponse({"error": "request method not allowed"}, status=status.HTTP_400_BAD_REQUEST)
    cli = boto3.client(**settings.BAISHANYUN_CONFIGS)  # 获得客户端会话对象

    file = request.FILES['myFileName']
    assert isinstance(file, UploadedFile)  # 获取到的文件信息应为一个UploadedFile对象

    name, file_type = file.name.rsplit(".", 1)
    if file_type not in ("jpg", "jpeg", "png", "doc", "docx", "pptx", "ppt", "xlsx", "xls"):
        error = {"error": "文件格式不合法，目前图片只支持:jpeg, jpg, png; 文档支持:doc, docx, pptx, ppt; "
                          "表格支持:xlsx和xls"}
        return JsonResponse(error, status=status.HTTP_400_BAD_REQUEST)

    data = file.read()
    key = get_md5(data)
    cli.put_object(
        ACL='public-read',  # 公共可读
        Bucket='minioss',  # 固定
        Key=f"oa/{key}.{file_type}",  # 文件保存在oa目录下
        ContentType=f'image/{file_type}',
        Body=data
    )
    url = f'http://s2.i.qingcdn.com/minioss/oa/{key}.{file_type}'
    data = {"name": name, "url": url}
    # return HttpResponse(json.dumps(data))
    return JsonResponse(data=data, status=status.HTTP_200_OK)
