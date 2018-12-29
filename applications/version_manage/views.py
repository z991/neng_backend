import json
import datetime
import operator

from datetime import date
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, list_route, detail_route
from rest_framework.response import Response

from applications.log_manage.models import OperateLog
from applications.setup.permissions import VersionProductPermission, VersionPermission
from ldap_server.configs import EMAIL_LIST, version_classic, version_pro
from libs.email_ali import Email_base
from libs.datetimes import date_to_str
from applications.version_manage.models import VersionRepository, VersionProduct
from .serializers import VersionProductSerializer, VersionRepositorySerializer
from applications.log_manage.views import VersionLog
from applications.log_manage.models import OperateLog, DetailLog

class VersionProductManage(viewsets.ModelViewSet):
    queryset = VersionProduct.objects.all().order_by("-id")
    serializer_class = VersionProductSerializer
    permission_classes = [VersionProductPermission, ]

    def get_queryset(self):
        queryset = VersionProduct.objects.all().order_by('-id')
        version_id = self.request.GET.get('version_id', "").strip()
        id = self.request.GET.get('id', "").strip()

        if version_id:
            queryset = queryset.filter(version_id=version_id)
        if id:
            queryset = queryset.filter(pk=id)

        return queryset, version_id

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(VersionProductManage, self).create(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data
        pk = kwargs.get("pk")
        version_product = VersionProduct.objects.get(pk=pk)
        version_product.version_id = VersionRepository.objects.get(pk=data["version_id"])
        version_product.product_classify = data.get("product_classify")
        version_product.product_name = data.get("product_name")
        version_product.product_version = data.get("product_version")
        version_product.release_date = data.get("release_date")
        version_product.product_explain = data.get("product_explain")
        if not data.get("release_number"):
            version_product.release_number = '0'
        else:
            version_product.release_number = data.get("release_number")
        version_product.save()
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)


    def list(self, request, *args, **kwargs):
        queryset, version_id = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for da in data:
            da["schedule"] = eval(da["schedule"])
        """
        如果version_id不为空，返回version_id
        """
        if version_id != '':
            # 获取改动记录
            query_params = {"operationmodule": "版本流程", "action": 3, "title": version_id}
            version_log = OperateLog.objects.filter(**query_params)
            # 查询基础日志列表
            base_list = []
            for version in version_log:
                user = version.user.last_name
                time = date_to_str(version.operationtime, format='%Y-%m-%d %H:%M:%S')
                log_id = version.id
                query_detail = DetailLog.objects.filter(log_id_id=log_id)
                for v in query_detail:
                    name = v.name
                    type = v.word
                    old_value = v.old_value
                    new_value = v.new_value
                    base_list.append({"user": user, "time": time,
                                      "modify_list": {"name": name, "type": type, "old_value": old_value, "new_value": new_value}})
            base_sort = sorted(base_list, key=operator.itemgetter('time'), reverse=True)
        else:
            base_sort = []

        result = {"version_info": data, "log": base_sort}
        return Response(result)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        ret = VersionProduct.objects.filter(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(['PUT'])
    def put_schedule(self, request, pk=None, *args, **kwargs):
        """
        修改产品版本进度
        :param request:
        :param pk:产品版本id
        :param args:
        :param kwargs:
        :return:
        """
        """
        [{"name": "项目立项","time": "%s","mileage": "1","index": 1, "course": ""},
        {"name": "产品设计","time": "","mileage": "0","index": 2,"course": ""},
        {"name": "研发","time": "","mileage": "","index": 3,"course": ""},
        {"name": "测试","time": "","mileage": "","index": 4,},
        {"name": "产品验收","time": "","mileage": "","index": 5},
        {"name": "部署","time": "","mileage": "","index": 6},
        {"name": "发版","time": "","mileage": "","index": 7},
        {"button_log": {"old": "无","new": "无"},"index": 8}]

        0：初始
        1：完成
        2: 驳回
        3: 被驳回
        4: 冒烟
        """
        data = request.data
        step = data.get("step")
        button = data.get("button")

        versionproduct = VersionProduct.objects.get(pk=pk)
        # 产品名称
        product_name = versionproduct.product_name
        version_id = versionproduct.version_id.id

        # 获取该产品的当前版本进度
        sche = eval(versionproduct.schedule)

        sche = sorted(sche, key=operator.itemgetter('index'), reverse=False)
        # 获取当前时间
        pro_time = date_to_str(datetime.datetime.now(), format='%Y-%m-%d %H:%M:%S')

        if step == '产品设计':
            if button == "评审通过":
                sche[1]["mileage"] = '1'
                sche[1]["time"] = pro_time

                sche[2]["mileage"] = '0'

        elif step == '研发':
            if button == "提测":
                sche[2]["mileage"] = '1'
                sche[2]["time"] = pro_time

                sche[3]["mileage"] = '0'

        elif step == '测试':
            if button == "驳回":
                sche[3]["mileage"] = '2'
                sche[3]["time"] = pro_time

                sche[2]["mileage"] = '3'

            elif button == "冒烟通过":
                sche[3]["mileage"] = '4'
                sche[3]["time"] = pro_time
            elif button == "通过":
                sche[3]["mileage"] = '1'
                sche[3]["time"] = pro_time

                sche[4]["mileage"] = '0'
        elif step == '产品验收':
            if button == "驳回":
                sche[4]["mileage"] = '2'
                sche[4]["time"] = pro_time

                sche[3]["mileage"] = '3'

            elif button == "通过":
                sche[4]["mileage"] = '1'
                sche[4]["time"] = pro_time

                sche[5]["mileage"] = '0'
        elif step == '部署':
            if button == "确认":
                sche[5]["mileage"] = '1'
                sche[5]["time"] = pro_time

                sche[6]["mileage"] = '0'

        elif step == '发版':
            if button == "发版":
                sche[6]["mileage"] = '1'
                sche[6]["time"] = pro_time
                versionproduct.release_status = True

        sche[-1]["button_log"]["old"] = sche[-1]["button_log"]["new"]
        sche[-1]["button_log"]["new"] = button
        versionproduct.schedule = sche
        versionproduct.save()

        # 记录版本变更
        VersionLog.change_status(request, sche, step, product_name, version_id)
        return Response({"info": "状态变更成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    def set_time(self, request, pk=None, *args,**kwargs):
        """
        版本进度里程时间设置
        :param request:
        :param pk: 产品版本id
        :return:
        """
        data = request.data
        step = data.get("step")
        # 里程
        course = data.get("course")
        versionproduct = VersionProduct.objects.get(pk=pk)
        sche = eval(versionproduct.schedule)

        for s in sche:
            name = s.get("name")
            if step == name:
                s["course"] = course
            else:
                continue

        versionproduct.schedule = sche
        versionproduct.save()
        return Response({"info": "里程设置成功"}, status=status.HTTP_200_OK)


class VersionRepositoryManage(viewsets.ModelViewSet):
    queryset = VersionRepository.objects.all().order_by("-id")
    serializer_class = VersionRepositorySerializer
    permission_classes = [VersionPermission, ]

    def sort_function(self, data):
        id_list = []
        new_data = []
        for item in data:
            id_list.append(item['id'])
            if not item['parent']:
                item['lv'] = 1
                item['children'] = []
                new_data.append(item)
                for each in data:
                    if item['id'] == each['parent']:
                        item['children'].append(each)
                        each['children'] = []
                        for inner in data:
                            if each['id'] == inner['parent']:
                                each['children'].append(inner)

        # 按照version_id 降序
        new_list = sorted(new_data, key=lambda new_data: new_data['version_id'], reverse=True)

        return new_list

    def list(self, request, *args, **kwargs):
        queryset = VersionRepository.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        result = self.sort_function(serializer.data)
        return Response(result)

    @list_route(['GET'])
    def get_email_list(self, request):
        return Response(data=EMAIL_LIST, status=status.HTTP_200_OK)

    # 发版通知
    @list_route(['GET'])
    def release_notice(self, request):
        # 要发版的版本的id
        version_id = request.GET.get('version_id', '')
        release_detail = VersionProduct.objects.all().filter(version_id=version_id)\
            .select_related('version_id__version_id')\
            .values('product_name', 'product_classify', 'version_id__version_id', 'release_date', 'product_explain')

        return Response(data=release_detail, status=status.HTTP_200_OK)

    @list_route(['POST'])
    def handle_release_notice(self, request):
        params = request.body.decode('utf-8')
        result = json.loads(params)

        version_ids = result.get('version_id', '')
        product_id = result.get('product_id', '')

        query = []
        if version_ids:
            query = VersionProduct.objects.all().filter(version_id=version_ids)
        if product_id:
            query = VersionProduct.objects.all().filter(pk=product_id)
        if query:
            for instance in query:
                instance.release_status = True
                instance.release_date = date.today()
                instance.save()
        # 收件人地址或是地址列表，支持多个收件人，最多30个
        recipients_list = result.get('recipients_list', '')
        # 自定义信件主题
        theme = result.get('theme', '')
        # 自定义发信昵称
        nickname = result.get('nickname', '')
        # 自定义HTML邮件内容
        content = result.get('content', '')
        client = Email_base()
        client.email(rcptto=recipients_list, theme=theme, nickname=nickname, content=content)
        return Response(data=[], status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        version_id = VersionRepository.objects.all().filter(parent=kwargs['pk'])
        if version_id:
            return Response({'error': '该版本还有子版本，请先删除子产品'}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return super(VersionRepositoryManage, self).destroy(request, *args, **kwargs)

    @list_route(['GET'])
    def classic_re(self, request, *args, **kwargs):
        data = self.request.query_params

        # 经典版
        if data["version"] == '1':
            return Response(version_classic, status=status.HTTP_200_OK)
        else:
            return Response(version_pro, status=status.HTTP_200_OK)
