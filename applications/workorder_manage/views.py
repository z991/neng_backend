import csv
import json
import codecs
import datetime
import time
import operator
import copy

from django.db import transaction
from django.http import HttpResponse
from libs.datetimes import str_to_date
from ldap_server.configs import title_dict
from rest_framework import status, viewsets
from rest_framework.response import Response
from libs.excel_base import Excel_export
from common.custom_exception import PushError
from libs.staion_msg_handle import station_msg_push
from django.views.decorators.csrf import csrf_exempt
from applications.log_manage.models import OperateLog, DetailLog
from applications.data_manage.models import OperatingRecord
from libs.classic_service.site_push import check_siteid_new,check_siteid_old, delsiteid
from applications.data_manage.views import SerGrpInquriesViewSet
from applications.production_manage.models import ServerGroup, Grid
from applications.setup.permissions import WorkOrderGroupPermission, CustomerKHKPermission
from rest_framework.decorators import detail_route, list_route, api_view
from libs.push_service_cg.Refactor_station_cg import StationData, RefactorStation
from ldap_server.configs import OPERATE_ACTION_CHOICES, STATUS_TYPES, PROD_SERV_VERSIONS, VERSION_ID, \
    FUNCTION_SELECT, STATION_CHOICES, CUSTOM_TYPES, BRAND_EFFECT_CHOICES, CUSTOMER_LEVEL_CHOICES, \
    TRAINING_METHOD_CHOICES, SPECIAL_SELECTION_CHOICES, TRANSMITTING_STATE_CHOICES, CLI_CHOICES, \
    LINK_TYPE_CHOICES, DEPLOY_WAYS
from applications.workorder_manage.models import OpenStationManage, Industry, AreaInfo, CompanyInfo, \
    StationInfo, CompanyAddress, CompanyUrl, ContactInfo, AccountConf, OrderManage, RemarkEvolve
from applications.production_manage.models import Grid, Product, SingleSelection, FunctionInfo
from applications.workorder_manage.serializers import OpenStationManageSerializer, IndustrySerializer, \
    AreaInfoSerializer, CompanyInfoSerializer, StationInfoSerializer, SimpOpenStationManageSerializer, \
    CustomerOpenStationManageSerializer, KHKCompanyInfoSerializer, KHKSmallCompanyInfoSerializer, \
    OrderManageSerializer, KHKCSCSerializer
from libs.classic_service.synchronous_function import BaseStart, Command, ForAllSynchronous, ForGridSynchronous, \
    ForSiteSynchronous
from libs.datetimes import date_to_str, compare_date
from applications.log_manage.views import OpenStationViewSet

today = datetime.date.today()


class CommonOpenSet:
    """
    把开站拆成了若干个小的模块，方便调用，避免代码冗余
    """
    def open_company_info(self, open, cmp_data):
        """
        公司基础信息创建
        :param open:  开站实例
        :param cmp_data: 前端传过来的公司字段信息
        :return:
        """
        company_url_list = cmp_data.pop('company_url')
        company_address = cmp_data.pop('company_address')
        industry = cmp_data.pop('industry')
        company_info = CompanyInfo.objects.create(open_station=open, **cmp_data)
        return company_info

    def open_url(self, company_info, company_url_list):
        """
        :param company_info: 公司信息的实例
        :param company_url_list:公司url列表
        :param method:默认是 0 :更新操作  1:新增操作
        :return:
        """
        CompanyUrl.objects.all().filter(company_info=company_info).delete()
        for url in company_url_list:
            com_url = CompanyUrl.objects.create(company_url=url['company_url'], company_info=company_info)
            com_url.save()
        return company_info

    def open_address(self, company_info, company_address):
        """
        公司地址的新增&变更
        :param company_info: 公司信息实例
        :param company_address: 前端传过来的公司地址
        :return:
        """
        # 如果该公司的地址已经存在（更改）
        if company_info.company_address:
            company_info.company_address.province = AreaInfo.objects.all().get(pk=company_address['province'])
            company_info.company_address.city = AreaInfo.objects.all().get(pk=company_address['city'])
            company_info.company_address.detail = company_address['detail']
            company_info.company_address.save()
        # 如果该公司的地址未创建
        else:
            province = AreaInfo.objects.all().get(pk=company_address['province'])
            city = AreaInfo.objects.all().get(pk=company_address['city'])
            com_ad = CompanyAddress.objects.all().create(company_info=company_info, province=province, city=city,
                                                         detail=company_address['detail'])
            com_ad.company_info = company_info
            com_ad.save()

    def open_company_some(self, cmp_data, company_info, sta_data):
        """
        公司信息的其他变更
        :param cmp_data: 前端传过来的公司信息
        :param company_info: 公司信息实例
        :param station_info: 站点信息实例
        :param sta_data: 前端传过来的站点信息
        :return:
        """
        # industry
        company_info.industry = Industry.objects.all().get(industry=cmp_data.get('industry'))
        company_info.station_type = cmp_data.get('station_type', company_info.station_type)
        company_info.company_name = cmp_data.get('company_name', company_info.company_name)
        company_info.abbreviation = cmp_data.get('abbreviation', company_info.abbreviation)

        company_info.company_email = cmp_data.get('company_email', company_info.company_email)
        company_info.GSZZ = cmp_data.get('GSZZ', company_info.GSZZ)
        company_info.customer_type = cmp_data.get('customer_type', company_info.customer_type)
        company_info.service_area = cmp_data.get('service_area', company_info.service_area)
        # company表和station表中的cli_version数据一致
        company_info.cli_version = sta_data.get('cli_version')
        company_info.classify = sta_data.get('classify')
        company_info.deploy_way = sta_data.get('deploy_way')
        company_info.save()
        return company_info

    def open_contact(self, company=None, link_info_list=None, method=0):
        """

        :param company: 公司实例
        :param link_info_list: 前端传过来的联系人数据
        :param method: 默认是 0 :更新操作  1:新增操作
        :return:
        """
        if method == 0:
            ret = ContactInfo.objects.all().filter(company=company).delete()
        for link_info in link_info_list:
            ContactInfo.objects.create(company=company, **link_info)
        return open

    def open_create_station(self, open, sta_data):
        """
        站点信息新增
        :param open: 开站实例
        :param sta_data: 前端传过的站点信息
        :return:
        """
        grid = sta_data.pop('grid')
        pact_products_list = sta_data.pop('pact_products')

        sta_data['classify'] = int(sta_data['classify'])
        station_info = StationInfo.objects.create(open_station=open, **sta_data)
        station_info.grid = Grid.objects.all().get(id=grid)
        station_info.version_id = sta_data.get("version_id")

        # pact_products
        for product in pact_products_list:
            station_info.pact_products.add(Product.objects.all().get(id=product))
        station_info.save()
        return station_info

    def open_update_station(self, open, station_info, sta_data, parents):
        """
        修改父站和子站共同的站点信息
        :param open: 开站的实例
        :param station_info: 站点信息的实例
        :param sta_data:前端传过来的站点信息
        :return:
        """
        # 父站
        if parents == 0:
            grid = sta_data.get('grid')
            station_info.cli_version = sta_data.get('cli_version', station_info.cli_version)
            station_info.classify = int(sta_data.get('classify', station_info.classify))
            station_info.deploy_way = sta_data.get('deploy_way', station_info.deploy_way)
            station_info.sales = sta_data.get('sales', station_info.sales)
            station_info.pre_sales = sta_data.get('pre_sales', station_info.pre_sales)
            station_info.oper_cslt = sta_data.get('oper_cslt', station_info.oper_cslt)
            station_info.impl_cslt = sta_data.get('impl_cslt', station_info.impl_cslt)
            station_info.oper_supt = sta_data.get('oper_supt', station_info.oper_supt)
            # grid
            station_info.grid = Grid.objects.all().get(id=grid)
        pact_products_list = sta_data.get('pact_products')

        station_info.validity_days = sta_data.get('validity_days', station_info.validity_days)
        station_info.open_station_time = sta_data.get('open_station_time', station_info.open_station_time)
        station_info.close_station_time = sta_data.get('close_station_time', station_info.close_station_time)
        station_info.open_station = open
        # 关联产品修改
        station_info.pact_products.clear()
        for product in pact_products_list:
            station_info.pact_products.add(Product.objects.all().get(id=product))
        station_info.save()

        return station_info

    def open_funclist(self, open, func_list):
        """
        :param open: 开站实例
        :param func_list: 前端传过来的功能开关
        :return:
        """
        open.func_list.clear()
        for prod_selc in func_list:
            # 单选框
            if prod_selc['id']:
                for selc in prod_selc['id']:
                    open.func_list.add(SingleSelection.objects.all().get(pk=selc))
            # 文本框
            for txt in prod_selc['ipu']:
                func = FunctionInfo.objects.all().get(pk=txt['id'])
                text = SingleSelection.objects.create(function=func, select_name=txt['value'],
                                                      select_value=txt['value'])
                text.save()
                open.func_list.add(text)
        return open

    def open_account(self, open, account_conf_list):
        """
        账户信息
        :return:
        """
        AccountConf.objects.all().filter(station=open).delete()

        for account_conf in account_conf_list:
            if "sure_pwd" in account_conf:
                account_conf.pop("sure_pwd")
            AccountConf.objects.create(station=open, **account_conf)
        return open

    def open_servergrouup(self, station_info, sta_data, classify):
        """
        (只有经典版才进行)获取传入的节点名称和修改前的节点名称，对比，若不同，则获取新节点下的访问量最少的服务组对象
        :param station_info: 站点信息实例
        :param sta_data: 前端传过来的站点信息
        :return:
        """

        input_grid_id = sta_data.get("grid", "")
        if int(classify) == 1:
            pre_grid_id = station_info.grid
            pre_server_grp = getattr(station_info, 'server_grp_id', None)
            if (input_grid_id != pre_grid_id) or (pre_server_grp is None):
                server_grp_name = SerGrpInquriesViewSet.min_sergrp_inquries(input_grid_id)
                server_grp = ServerGroup.objects.all().filter(group_name=server_grp_name).first()
                station_info.server_grp = server_grp
                station_info.save()
        return station_info

    def get_classify(self, pk):
        """
        获取该开站的版本类型和父站
        :param pk:开站的id
        :return:
        """
        its_parent = OpenStationManage.objects.get(pk=pk).its_parent
        # 父站
        if its_parent == None:
            classiy = StationInfo.objects.filter(open_station=pk).first().classify

        else:
            open_parents = OpenStationManage.objects.get(pk=its_parent)
            classiy = StationInfo.objects.filter(open_station=open_parents).first().classiy
        return classiy

    def open_renewal(self, pre_station_info, company_id, sta_data):
        """
        续费客户记录
        :param pre_station_info: 修改前的站点到期时间和产品名称列表
        :param company_id: 企业id
        :param sta_data: 前端传过来的站点信息
        :return:
        """
        # 获取本次请求传入的站点到期时间和产品名称列表
        input_close_station_time = str_to_date(sta_data['close_station_time'])
        # 将续费客户记录写入统计表中
        if input_close_station_time != pre_station_info[0][1]:
            OperatingRecord.record_renewal(company_id)

    def new_product(self, company_id, pre_station_info, input_pact_products):
        """
        客户产品记录
        :param company_id: 企业id
        :param pre_station_info: 修改前的站点到期时间和产品名称列表
        :param input_pact_products: 前端传过来的产品列表
        :return:
        """
        # 用来记录产品客户记录
        pre_station_dict = dict(pre_station_info)
        for each in input_pact_products:
            if each not in pre_station_dict.keys():
                OperatingRecord.record_add_product(company_id)

    def open_manage(self, company_id, online_status, classify):
        """
        开站
        :param company_id: 企业id
        :param online_status: 开站状态
        :param classify: 站点版本
        :return:
        """
        if int(classify) == 1 and online_status is True:
            try:
                station_msg_push(company_id, online_status, 1)

            except PushError as p:
                if p.value.startswith('11'):
                    return Response({'error': p.value.lstrip('11')}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': '消息推送失败'}, status=status.HTTP_400_BAD_REQUEST)
        elif int(classify) == 2 and online_status is True:
            station_msg_push(company_id, online_status, 2)
        return company_id


class OpenStationManageSet(viewsets.ModelViewSet):
    queryset = OpenStationManage.objects.all().filter(its_parent__isnull=True).order_by('-id')
    permission_classes = [WorkOrderGroupPermission]

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return SimpOpenStationManageSerializer
        elif self.action == 'customer':
            return CustomerOpenStationManageSerializer
        else:
            return OpenStationManageSerializer

    @list_route(methods=['get'])
    def customer(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(OpenStationManageSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def get_version_choice(self, request):
        data_list = list(VERSION_ID)
        data = []
        for item in data_list:
            data.append({'value': item[1], 'key': item[0]})
        return Response(status=status.HTTP_200_OK, data=data)

    def get_queryset(self):
        company_name = self.request.GET.get('company_name', "").strip()  #
        station_type = self.request.GET.get('station_type', "").strip()
        deploy_way = self.request.GET.get('deploy_way', "").strip()
        cli_version = self.request.GET.get('cli_version', "").strip()
        abbreviation = self.request.GET.get('abbreviation', "").strip()
        company_id = self.request.GET.get('company_id', "").strip()
        online_status = self.request.GET.get('online_status', "").strip()
        order_work = self.request.GET.get('order_work', "").strip()
        grid_name = self.request.GET.get('grid_name', "").strip()
        industry = self.request.GET.get('industry', "").strip()
        open_collation = self.request.GET.get('open_station_time', "").strip()
        close_collation = self.request.GET.get('close_station_time', "").strip()
        # 是否为父类 空：父类站点  其他：子类站点
        its_parent = self.request.GET.get("its_parent", '0').strip()
        # 子站
        if its_parent != "''" and its_parent != '0':
            queryset = OpenStationManage.objects.all().filter(its_parent=its_parent).order_by('-id')
        # 父站
        else:
            queryset = OpenStationManage.objects.all().filter(its_parent__isnull=True).order_by('-id')

        if company_name:  # 公司名称查询
            queryset = queryset.filter(company_info__company_name__icontains=company_name)
        if abbreviation:  # 公司简称查询
            queryset = queryset.filter(company_info__abbreviation=abbreviation)
        if company_id:  # 企业id查询
            queryset = queryset.filter(station_info__company_id__icontains=company_id)
        if station_type:  # 站点类型查询
            queryset = queryset.filter(company_info__station_type=station_type)
        if online_status:  # 上线状态查询
            queryset = queryset.filter(online_status=online_status)
        if deploy_way:  # 部署方式查询
            queryset = queryset.filter(station_info__deploy_way=deploy_way)
        if cli_version:  # 客户版本查询
            queryset = queryset.filter(station_info__cli_version=cli_version)
        if order_work:  #开站标识（判断来自订单还是来自开站页面）
            queryset = queryset.filter(station_info__order_work=order_work)
        if grid_name:  #节点查询
            queryset = queryset.filter(station_info__grid__grid_name__icontains=grid_name)
        if industry:   #行业查询
            queryset = queryset.filter(company_info__industry__industry__icontains=industry)

        if close_collation == '0':
            queryset = queryset.order_by('-station_info__close_station_time')
        if close_collation == '1':
            queryset = queryset.order_by('station_info__close_station_time')

        if open_collation == '0':
            queryset = queryset.order_by('-station_info__open_station_time')
        if open_collation == '1':
            queryset = queryset.order_by('station_info__open_station_time')
        return queryset

    @list_route(['GET'])
    def get_station_info(self, request):
        """
        开站导出
        :param request:
        :return:
        https://docs.djangoproject.com/en/1.11/howto/outputting-csv/
        """
        # 过滤条件
        filter_list = request.GET.getlist("filter", "")
        # 节点
        grid = request.GET.get("grid", "").strip()
        # 行业
        industry = request.GET.get("industry", "").strip()
        # 父站or子站
        its_parent = request.GET.get("its_parent", "0").strip()

        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type="text/csv;charset=utf-8")
        response['Content-Disposition'] = 'attachment; filename=OpenStation_Manage_Info.csv'
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow([f"云平台-站点信息", today])

        for i in filter_list:
            if i == "":
                filter_list.remove(i)
        if grid:
            queryset = queryset.filter(station_info__grid__id=grid)
        if industry:
            queryset = queryset.filter(company_info__industry__industry=industry)
        # 初始导出字段
        init_list = ["id", 'company_info__company_name', 'station_info__company_id',
                           'company_info__industry__industry', 'station_info__grid__grid_name']
        # 父站全部导出
        if len(filter_list) == 0 and its_parent == "0":
            init_list = ['id', 'online_status', 'company_info__station_type', 'company_info__industry__industry',
                            'company_info__company_name', 'station_info__company_id', 'station_info__grid__grid_name',
                            'station_info__classify', 'station_info__deploy_way', 'station_info__cli_version',
                            'station_info__open_station_time', 'station_info__close_station_time',
                            'station_info__order_work']
        # 父站部分字段导出
        elif len(filter_list) != 0 and its_parent == "0":
            init_list.extend(filter_list)
        # 子站全部字段导出
        if its_parent != "0":
            queryset = queryset.filter(its_parent=its_parent)
            init_list = ['id', 'online_status', 'company_info__station_type', 'company_info__industry__industry',
                        'company_info__company_name', 'station_info__company_id', 'station_info__close_station_time']
        old_result = queryset\
            .select_related('id', 'online_status', 'company_info__industry__industry',
                            'company_info__company_name', 'station_info__company_id',
                            'station_info__open_station_time', 'station_info__close_station_time')\
            .values(*init_list)

        first_row = []
        num = 1
        for ret in old_result:

            result = data_cleaning(ret)
            if not first_row:

                info_row = list(result.keys())
                for each in info_row:
                    title = title_dict[each]
                    first_row.append(title)
                writer.writerow(first_row)
            data_row = list(result.values())

            data_row[0] = num
            num += 1

            writer.writerow(data_row)
        return response

    @list_route(['GET'])
    def derived_field(self, request):
        """
        告诉前端可以导出的字段
        :param request:
        :return:
        """
        date_list = list()
        keys = ["id", "company_info__company_name", "station_info__company_id", "company_info__industry__industry", "station_info__grid__grid_name"]
        date = {date_list.append({"name": key, "field": title_dict[key]}) for key in title_dict if key not in keys}
        date_list.append(date)
        return Response(data=date_list, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def modify_status(self, request, pk=None, *args, **kwargs):
        site = OpenStationManage.objects.all().get(pk=pk)
        company_id = site.station_info.company_id
        input_online_status = request.data.get('online_status', None)
        if input_online_status is None:
            return Response({'error': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)

        # 变更客户库的流转状态
        company_instance = site.company_info
        if input_online_status is True:
            company_instance.transmitting_state = 3

        elif input_online_status is False:
            company_instance.transmitting_state = 0

        company_instance.save()
        # 前端发送请求时未判断状态是否改变，所以，为减少对数据库不必要的读写，上线状态没变则直接返回
        if input_online_status == site.online_status:
            return Response(status=status.HTTP_200_OK)
        try:
            with transaction.atomic():
                site.online_status = input_online_status
                site.save()
                station_msg_push(site.station_info.company_id,site.online_status,site.station_info.classify)
        except PushError as p:
            if p.value.startswith('11'):
                return Response({'error': p.value.lstrip('11')}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': '消息推送失败'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            OpenStationViewSet.create_base_log(request, company_id, "开站管理", 500)
            # 如果新的上线状态为True，则将上线记录写入统计表
            if input_online_status:
                OperatingRecord.record_online(company_id)

            # 如果新的上线状态为False,则将下线记录写入统计表
            else:
                OperatingRecord.record_offline(company_id)

            return Response(status=status.HTTP_200_OK)

    @list_route(['GET'])
    def modify_time(self, request):
        """
        批量修改子站时间
        :param request:
        :return:
        """
        # 要修改到期时间的企业的id
        company_id = request.GET.getlist("company_id")
        # 到期时间
        date = request.GET.get("date")
        try:
            with transaction.atomic():
                for company in company_id:
                    OpenStationViewSet.create_base_log(request, company_id, "开站管理", 500)
                    open_station = StationInfo.objects.get(company_id=company)
                    open_station.close_station_time = str_to_date(date)
                    open_station.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"info": "修改成功"}, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def verify_company_id(self, request):
        company_id = request.GET.get('company_id', '').strip()
        grid_id = request.GET.get('grid_id', '').strip()
        version = request.GET.get('version', '').strip()
        if not (company_id and grid_id and version):
            return Response({'error': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        if OpenStationManage.objects.all().filter(station_info__company_id=company_id):
            return Response({'error': '企业id重复'}, status=status.HTTP_400_BAD_REQUEST)
        success_old = check_siteid_old(siteid=company_id)
        success_new = check_siteid_new(siteid=company_id)
        if not success_old or not success_new:
            return Response({"error": "线上该企业已存在"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def copy_open(self, request):
        """
        复制站点
        :param request:
        :return:
        """
        try:
            grid = request.GET.get("grid", "")
            # 企业id
            company_id = request.GET.get("company_id", "")
            # id
            id = request.GET.get("id", "")
            with transaction.atomic():
                # 节点id
                open_station = OpenStationManage.objects.get(pk=id)

                # company_info相关
                company_info = open_station.company_info
                company_address = company_info.company_address

                # 新增公司地址
                try:
                    province = company_address.province
                    city = company_address.city
                    detail = company_address.detail
                    address = CompanyAddress.objects.create(province=province, city=city, detail=detail)
                except:
                    address = 0

                company_dict = {
                    "station_type": company_info.station_type,
                    "company_name": company_info.company_name,
                    "company_address": address,
                    "abbreviation": company_info.abbreviation,
                    "cli_version": company_info.cli_version,
                    "deploy_way": company_info.deploy_way,
                    "classify": company_info.classify,
                    "company_email": company_info.company_email,
                    "industry": company_info.industry,
                    "GSZZ": company_info.GSZZ,
                    "customer_type": company_info.customer_type,
                    "service_area": company_info.service_area,
                }
                if address == 0:
                    del company_dict["company_address"]

                # 新增企业信息
                company_create = CompanyInfo.objects.create(**company_dict)

                company_address = company_info.company_url.all()
                for address in company_address:
                    # 新增公司url
                    ret = CompanyUrl.objects.create(company_url=address.company_url, company_info=company_create)

                # station_info相关新增
                station_info = open_station.station_info

                grid_get = Grid.objects.get(pk=grid)

                station_dict = {
                    "company_id": company_id,
                    "validity_days": station_info.validity_days,
                    "grid": grid_get,
                    "server_grp": station_info.server_grp,
                    "cli_version": station_info.cli_version,
                    "deploy_way": company_info.deploy_way,
                    "classify": company_info.classify,
                    "open_station_time": station_info.open_station_time,
                    "close_station_time": station_info.close_station_time,
                    "sales": station_info.sales,
                    "pre_sales": station_info.pre_sales,
                    "oper_cslt": station_info.oper_cslt,
                    "impl_cslt": station_info.impl_cslt,
                    "oper_supt": request.user.last_name,
                    "order_work": station_info.order_work,
                    "set_up": station_info.set_up,
                    "version_id": station_info.version_id
                }

                station_create = StationInfo.objects.create(**station_dict)
                # 合同产品
                pact_products_list = station_info.pact_products.all()
                for product in pact_products_list:
                    station_create.pact_products.add(product)

                open_dict = {
                    "online_status": open_station.online_status,
                    "company_info": company_create,
                    "station_info": station_create
                }
                open_create = OpenStationManage.objects.create(**open_dict)

                # 功能开关
                func_list = open_station.func_list.all()
                for func in func_list:
                    open_create.func_list.add(func)

                # link_info
                link_info = open_station.link_info.all()
                for link in link_info:
                    link_dict = {
                        "linkman": link.linkman,
                        "link_phone": link.link_phone,
                        "link_email": link.link_email,
                        "link_qq": link.link_qq,
                        "station": open_create,
                        "company": company_info,
                    }
                    link_create = ContactInfo.objects.create(**link_dict)

                #AccountConf 账户相关信息
                account_info = open_station.account_conf.all()
                for account in account_info:
                    account_dict = {
                        "user_name": account.user_name,
                        "set_pwd": account.set_pwd,
                        "station": open_create
                    }
                    account_create = AccountConf.objects.create(**account_dict)
        except Exception as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        OpenStationViewSet.create_base_log(request, company_id, "开站管理", 500)
        return Response(data={"info": "复制成功"}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def get_pact_products(self, request, pk=None, *args, **kwargs):
        site = self.get_object()
        ret = {'data': []}
        pact_products = site.station_info.pact_products.all().values_list('product', flat=True)
        ret['data'] = list(pact_products)
        return Response(ret, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        function：创建开站对象
        describe：用serializer的create将开站数据录入库,增加根据昨日该节点下各服务组咨询量，取咨询量最少的，为站点指定服务组
        date：20171130
        author：gzh
        version:1.10
        """
        open_data = request.body

        open_data = str(open_data, encoding="utf-8")
        open_data = json.loads(open_data)
        company_id = open_data['station_info']['company_id']
        open_data['company_info']['cli_version'] = open_data['station_info']['cli_version']
        open_data['company_info']['classify'] = open_data['station_info']['classify']
        open_data['company_info']['deploy_way'] = open_data['station_info']['deploy_way']

        grid_id = open_data['station_info']['grid']
        if int(open_data['station_info']['classify']) == 1:
            server_grp_name = SerGrpInquriesViewSet.min_sergrp_inquries(grid_id)
            server_grp = ServerGroup.objects.all().filter(group_name=server_grp_name).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                self.perform_create(serializer)
                site = serializer.instance
                if int(open_data['station_info']['classify']) == 1:
                    site.station_info.server_grp = server_grp
                site.station_info.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 将新增客户记录写入统计表中
            OperatingRecord.record_create(company_id)

        return Response({"site": site.id}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        open_data = request.data
        """
        原serializer update方法代码,修改接口url变更后无法找到serializer的update方法，所以就把serializer的update注释掉了
        """
        # 判断更改的是否为子站， 如果为空，不是子站，否则是子站
        its_parent = open_data["its_parent"]
        try:
            with transaction.atomic():
                """
                公司信息
                """
                cmp_data = open_data['company_info']
                company_info = instance.company_info
                company_url_list = cmp_data.get('company_url')

                company_address = cmp_data.get('company_address')
                industry = cmp_data.get('industry')

                # compcany_url
                CompanyUrl.objects.all().filter(company_info=company_info).delete()
                for url in company_url_list:
                    com_url = CompanyUrl.objects.create(company_url=url['company_url'], company_info=company_info)
                    com_url.save()

                # company_address
                if company_info.company_address:
                    company_info.company_address.province = AreaInfo.objects.all().get(pk=company_address['province'])
                    company_info.company_address.city = AreaInfo.objects.all().get(pk=company_address['city'])
                    company_info.company_address.detail = company_address['detail']
                    company_info.company_address.save()
                else:
                    province = AreaInfo.objects.all().get(pk=company_address['province'])
                    city = AreaInfo.objects.all().get(pk=company_address['city'])
                    com_ad = CompanyAddress.objects.all().create(company_info=company_info, province=province, city=city,
                                                                 detail=company_address['detail'])
                    com_ad.company_info = company_info
                    com_ad.save()

                # industry
                company_info.industry = Industry.objects.all().get(industry=industry)
                company_info.station_type = cmp_data.get('station_type', company_info.station_type)
                company_info.company_name = cmp_data.get('company_name', company_info.company_name)
                company_info.abbreviation = cmp_data.get('abbreviation', company_info.abbreviation)

                company_info.company_email = cmp_data.get('company_email', company_info.company_email)
                company_info.GSZZ = cmp_data.get('GSZZ', company_info.GSZZ)
                company_info.customer_type = cmp_data.get('customer_type', company_info.customer_type)
                company_info.service_area = cmp_data.get('service_area', company_info.service_area)
                # company表和station表中的cli_version数据一致
                company_info.cli_version = open_data['station_info'].get('cli_version',
                                                                         instance.station_info.cli_version)
                company_info.classify = open_data['station_info'].get('classify', instance.station_info.classify)
                company_info.deploy_way = open_data['station_info'].get('deploy_way', instance.station_info.deploy_way)
                company_info.save()
                """
                联系人信息
                """
                # link_info
                ContactInfo.objects.all().filter(station=instance).delete()
                link_info_list = open_data['link_info']
                for link_info in link_info_list:
                    ContactInfo.objects.create(station=instance, **link_info)

                """
                站点信息
                """
                sta_data = open_data['station_info']
                pact_products_list = sta_data.get('pact_products')
                station_info = instance.station_info

                station_info.validity_days = sta_data.get('validity_days', station_info.validity_days)
                station_info.open_station_time = sta_data.get('open_station_time', station_info.open_station_time)
                station_info.close_station_time = sta_data.get('close_station_time', station_info.close_station_time)

                # 如果its_parent 为空，修改的是父站信息
                if not its_parent:
                    grid = sta_data.get('grid')
                    station_info.cli_version = sta_data.get('cli_version', station_info.cli_version)
                    station_info.classify = int(sta_data.get('classify', station_info.classify))
                    station_info.deploy_way = sta_data.get('deploy_way', station_info.deploy_way)
                    station_info.sales = sta_data.get('sales', station_info.sales)
                    station_info.pre_sales = sta_data.get('pre_sales', station_info.pre_sales)
                    station_info.oper_cslt = sta_data.get('oper_cslt', station_info.oper_cslt)
                    station_info.impl_cslt = sta_data.get('impl_cslt', station_info.impl_cslt)
                    station_info.oper_supt = sta_data.get('oper_supt', station_info.oper_supt)
                    # grid
                    station_info.grid = Grid.objects.all().get(id=grid)

                station_info.open_station = instance
                # pact_products
                station_info.pact_products.clear()
                for product in pact_products_list:
                    station_info.pact_products.add(Product.objects.all().get(id=product))
                station_info.save()

                """
                功能开关表信息
                """
                # func_list
                instance.func_list.clear()
                prod_selc_list = open_data['func_list']
                for prod_selc in prod_selc_list:
                    # 单选框
                    if prod_selc['id']:
                        for selc in prod_selc['id']:
                            instance.func_list.add(SingleSelection.objects.all().get(pk=selc))
                    # 文本框
                    for txt in prod_selc['ipu']:
                        func = FunctionInfo.objects.all().get(pk=txt['id'])
                        text = SingleSelection.objects.create(function=func, select_name=txt['value'],
                                                              select_value=txt['value'])
                        text.save()
                        instance.func_list.add(text)
                """
                账户配置信息
                """
                # account_conf
                AccountConf.objects.all().filter(station=instance).delete()
                account_conf_list = open_data['account_conf']

                for account_conf in account_conf_list:
                    if "sure_pwd" in account_conf:
                        account_conf.pop("sure_pwd")
                    AccountConf.objects.create(station=instance, **account_conf)

                instance.save()

                # 获取企业ID
                company_id = open_data['station_info']['company_id']
                # 获取本次请求传入的站点到期时间和产品名称列表
                input_close_station_time = str_to_date(open_data['station_info']['close_station_time'])
                input_pact_products = open_data['station_info']['pact_products']

                # 获取修改前的站点到期时间和产品名称列表
                pre_station_info = StationInfo.objects.filter(open_station__id=kwargs['pk']).select_related(
                    'pact_products__product').values_list('pact_products__product', 'close_station_time')
                # 用来记录产品客户记录
                pre_station_dict = dict(pre_station_info)

                input_grid_id = open_data['station_info'].get("grid", "")
                version_id = open_data['station_info'].get("version_id")

                # 获取传入的节点名称和修改前的节点名称，对比，若不同，则获取新节点下的访问量最少的服务组对象
                server_grp = ""
                if int(open_data['station_info']['classify']) == 1:
                    pre_grid_id = instance.station_info.grid
                    pre_server_grp = getattr(instance.station_info, 'server_grp_id', None)
                    if (input_grid_id != pre_grid_id) or (pre_server_grp is None):
                        server_grp_name = SerGrpInquriesViewSet.min_sergrp_inquries(input_grid_id)
                        server_grp = ServerGroup.objects.all().filter(group_name=server_grp_name).first()

                # 获取上线状态
                online_status = instance.online_status
                partial = kwargs.get('partial', False)

                serializer = self.get_serializer(instance, data=open_data, partial=partial)
                serializer.is_valid(raise_exception=True)

                instance.station_info.version_id = version_id
                instance.station_info.save()


                # 查看父站类型 经典or重构
                query_id = its_parent if its_parent else instance.id

                parents_classify = StationInfo.objects.filter(open_station__id=query_id).first().classify

                insc = instance.station_info.classify
                # 分经典版站点修改和重构版站点修改两种情况：流程---在保存完数据后，验证一下上线状态，若是上线，则调用推送接口；
                if instance.station_info.classify == 1 or parents_classify == 1:

                    # 父站经典版操作
                    try:
                        # self.perform_update(serializer)
                        if (input_grid_id != pre_grid_id) or (pre_server_grp is None):
                            instance.station_info.server_grp = server_grp
                            instance.station_info.save()
                        if online_status == True:
                            pass
                            station_msg_push(company_id, online_status, 1)
                    except PushError as p:
                        if p.value.startswith('11'):
                            return Response({'error': p.value.lstrip('11')}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'error': '消息推送失败'}, status=status.HTTP_400_BAD_REQUEST)
                elif (instance.station_info.classify == 2 or parents_classify == 2) and online_status == True:
                    station_msg_push(company_id, online_status, 2)
                    pass

                # 将续费客户记录写入统计表中
                if input_close_station_time != pre_station_info[0][1]:
                    OperatingRecord.record_renewal(company_id)

                # 将新增产品客户记录写入统计表中
                for each in input_pact_products:
                    if each not in pre_station_dict.keys():
                        OperatingRecord.record_add_product(company_id)
        except Exception as e:
            return Response({'error': e.args}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"info": "更新成功"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        kwargs = kwargs
        pk = kwargs.get("pk")
        company_id = obj.station_info.company_id
        its_parent = OpenStationManage.objects.get(pk=pk).its_parent

        # 子站
        if its_parent is not None:
            if delsiteid(obj.station_info.company_id):
                ret = OpenStationManage.objects.filter(pk=pk).delete()
            else:
                return Response({'error': '删除失败'}, status=status.HTTP_400_BAD_REQUEST)
        # 父站
        elif its_parent == None:
            if delsiteid(company_id):
                # 先删除子站
                OpenStationManage.objects.filter(its_parent=pk).delete()
                # 删除父站
                OpenStationManage.objects.get(pk=pk).delete()
            else:
                return Response({'error': '删除失败'}, status=status.HTTP_400_BAD_REQUEST)
        OpenStationViewSet.create_base_log(request, company_id, "开站管理", 2)
        return Response({'info': '删除成功'}, status=status.HTTP_200_OK)


class CompanyInfoSet(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.all().order_by("-id")
    serializer_class = CompanyInfoSerializer


class CompanyManageSet(viewsets.ModelViewSet):
    """
    客户库视图类
    """
    queryset = CompanyInfo.objects.all().order_by("-id")
    permission_classes = [CustomerKHKPermission]

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return KHKSmallCompanyInfoSerializer
        else:
            return KHKCompanyInfoSerializer

    def get_queryset(self):
        queryset = CompanyInfo.objects.all().order_by("-id")
        if self.request.method == 'PUT':
            pk = self.request.data.get('id')
            status = CompanyInfo.objects.all().filter(pk=pk).values_list('transmitting_state', flat=True)
            if status[0] == 0:
                queryset = CompanyInfo.objects.all().order_by("-transmitting_state")

        company_name = self.request.GET.get('company_name', "").strip()
        transmitting_state = self.request.GET.get('transmitting_state', "").strip()
        if company_name:
            queryset = queryset.filter(company_name__icontains=company_name)
        if transmitting_state:
            queryset = queryset.filter(transmitting_state=transmitting_state)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            for item in serializer.data:
                # 驳回理由
                comment = item['comment']
                if comment:
                    strr = comment.split('//linefeed//')
                    item['comment'] = dict(zip([n for n in range(len(strr))], strr))
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        for item in serializer.data:
            # 驳回理由
            comment = item['comment']
            if comment:
                strr = comment.split('//linefeed//')
                item['comment'] = dict(zip([n for n in range(len(strr))], strr))
        return Response(serializer.data)

    # 客户库导出  复用了列表页方法 参数相同
    @list_route(methods=['get'])
    def derive_khk(self, request):
        name = "生态云-客户库信息"
        title_key = ["id", "company_name", "deploy", "industry", "platform_informatiom", "start_date", "end_date"]
        title_value = ["id", "企业名称", "部署方式", "行业", "平台信息", "订单开始时间", "订单结束时间"]
        title = dict(zip(title_key, title_value))
        content_list = []

        queryset = self.get_khk_list(request, derive=1)
        if not queryset:
            content_list.append(dict(zip(title_key, [i-i for i in range(len(title_key))])))
            excl = Excel_export(filename=name, title=title, content=content_list)
            response = excl.export_csv()
            return response
        for item in queryset:
            inner_list = list(item.values())
            inner_dict = dict(DEPLOY_WAYS)
            inner_list[2] = inner_dict.get(inner_list[2])

            content_list.append(dict(zip(title_key, inner_list)))

        excl = Excel_export(filename=name, title=title, content=content_list)
        response = excl.export_csv()
        return response

    # 获取功能列表
    @list_route(methods=['get'])
    def get_function_config(self, request):
        return Response(dict(FUNCTION_SELECT))

    # 获取流转状态
    @list_route(methods=['get'])
    def get_transmitting_state(self, request):
        return Response(dict(TRANSMITTING_STATE_CHOICES))

    # 获取品牌效应
    @list_route(methods=['get'])
    def get_brand_effect(self, request):
        return Response(dict(BRAND_EFFECT_CHOICES))

    # 获取客户级别
    @list_route(methods=['get'])
    def get_customer_level(self, request):
        return Response(dict(CUSTOMER_LEVEL_CHOICES))

    # 获取培训方式
    @list_route(methods=['get'])
    def get_training_method(self, request):
        return Response(dict(TRAINING_METHOD_CHOICES))

    # 获取联系人类别
    @list_route(methods=['get'])
    def get_link_type(self, request):
        return Response(dict(LINK_TYPE_CHOICES))

    # 获取审批页
    @list_route(methods=['get'])
    def get_company_list(self, request):
        queryset = CompanyInfo.objects.all().order_by("-transmitting_state").filter(transmitting_state=1)

        company_name = request.GET.get('company_name', "").strip()

        cli_version = request.GET.get('cli_version', "").strip()
        industry = request.GET.get('industry', "").strip()

        if company_name:
            queryset = queryset.filter(company_name__icontains=company_name)
        if cli_version:
            queryset = queryset.filter(cli_version=cli_version)
        if industry:
            queryset = queryset.filter(industry__id=industry)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = KHKCSCSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = KHKCSCSerializer(queryset, many=True)
        return Response(serializer.data)

    # 获取审批通过的 客户库
    @list_route(methods=['get'])
    def get_khk_list(self, request, derive=0):
        queryset = CompanyInfo.objects.all().filter(transmitting_state=3).order_by('-id')

        company_name = request.GET.get('company_name', "").strip()
        deploy_way = request.GET.get('deploy_way', "").strip()
        industry = request.GET.get('industry', "").strip()
        page = request.GET.get('page', "1").strip()

        if company_name:
            queryset = queryset.filter(company_name__icontains=company_name)
        if deploy_way:
            queryset = queryset.filter(deploy_way=deploy_way)
        if industry:
            queryset = queryset.filter(industry__id=industry)

        serializer = queryset.select_related('order_info__contract_start_time', 'industry__industry',
                                             'order_info__contract_end_time',
                                             'order_info__contract_end_time')\
            .values('id', 'company_name', 'deploy_way', 'industry__industry', 'platform_informatiom',
                    'order_info__contract_start_time', 'order_info__contract_end_time')

        if not len(serializer):
            if derive:
                return []
            else:
                return Response([])

        # 是否导出
        if derive:
            return serializer

        big_page_num = int(str(int(len(serializer))/10).split('.')[0]) + 1

        if int(page) > big_page_num:
            return Response({'error': '超出最大页数'}, status=status.HTTP_400_BAD_REQUEST)

        front = (int(page) - 1) * 10
        back = int(page) * 10

        previous = int(page) - 1
        next_num = int(page) + 1

        page_num = {
            "next": next_num,
            "previous": previous,
            "current": int(page),
            "total_page": big_page_num,
            "total_count": len(serializer)
        }
        data = {}

        # 最后一页
        if int(page) == big_page_num:
            back = int(len(serializer))
            page_ser = serializer[front:back]
            page_num['next'] = 'null'
            data['page_num'] = page_num
            data['results'] = page_ser
            return Response(data)

        # 第一页
        if int(page) == 1:
            page_ser = serializer[front:back]
            page_num['previous'] = 'null'
            data['page_num'] = page_num
            data['results'] = page_ser
            return Response(data)

        page_ser = serializer[front:back]
        data['page_num'] = page_num
        data['results'] = page_ser
        return Response(data)

    # 提交驳回理由
    @list_route(methods=['post'])
    def reject_reason(self, request):
        # 驳回理由
        comment = request.data.get('comment')
        if comment:
            instance = CompanyInfo.objects.all().get(pk=request.data.get('id'))
            comment_content = instance.comment
            if comment_content:
                instance.comment = comment + '//linefeed//' + comment_content
                instance.save()
            else:
                instance.comment = comment
                instance.save()
        return Response(status=status.HTTP_200_OK)

    # 修改流转状态
    @list_route(methods=['get'])
    def status(self, request):
        company_id = request.GET.get('company_id')
        boole = request.GET.get('boole')

        transmitting_state = CompanyInfo.objects.get(pk=company_id).transmitting_state
        # 驳回
        if boole == '0':
            company_info = CompanyInfo.objects.all().filter(pk=company_id).update(transmitting_state=2)
        # 重新申请
        elif boole == '2':
            if transmitting_state != 2:
                return Response({"error": "该公司状态不是审批驳回，禁止申请"}, status=status.HTTP_400_BAD_REQUEST)
            company_info = CompanyInfo.objects.all().filter(pk=company_id).update(transmitting_state=1)

        return Response(company_info)

    @list_route(methods=['post'])
    def create_remark(self, request):
        """
        备注，进展，沟通新增接口
        :param request:
        :return:
        """
        data = request.data
        content = data.get("content")
        mark_type = data.get("mark_type")
        company_id = data.get("company")
        # company = CompanyInfo.objects.get(pk=company_id)

        user = request.user
        remark_dict = {
            "user": user,
            "content": content,
            "mark_type": mark_type,
            "correlation_id": company_id,
        }
        ret = RemarkEvolve.objects.create(**remark_dict)
        return Response(data={"info": "新增成功"}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def get_remark(self, request, pk=None, *args, **kwargs):
        # 1: 备注  2：改动记录 3：沟通
        mark_dict = {1: [], 2: [], 3: []}
        queryset = RemarkEvolve.objects.filter(mark_type__in=(1, 3), correlation_id=pk).order_by('-operationtime')
        for iterm in queryset:
            user = iterm.user.last_name
            operationtime = iterm.operationtime
            content = iterm.content
            type = iterm.mark_type
            mark_dict[type].append({"user": user, "time": date_to_str(operationtime, format='%Y-%m-%d %H:%M:%S'), "content": content})
        mark_dict[1] = sorted(mark_dict[1], key=operator.itemgetter('time'), reverse=True)
        mark_dict[3] = sorted(mark_dict[3], key=operator.itemgetter('time'), reverse=True)
        # 获取改动记录
        query_params = {"operationmodule": "客户库", "action": 3, "title": pk}
        query_base = OperateLog.objects.filter(**query_params)
        # 查询基础日志列表
        base_list = []
        for item in query_base:
            user = item.user.last_name
            time = date_to_str(item.operationtime, format='%Y-%m-%d %H:%M:%S')
            id = item.id
            query_detail = DetailLog.objects.filter(log_id=id)
            value_list = []
            for v in query_detail:
                name = v.name
                old_value = v.old_value
                new_value = v.new_value
                value_list.append({"name": name, "old_value": old_value, "new_value": new_value})
            base_list.append({"user": user, "time": time, "modify_list": value_list})
        # 根据时间排序，最新数据的在前面
        base_list = sorted(base_list, key=operator.itemgetter('time'), reverse=True)
        mark_dict[2] = base_list
        return Response(data=mark_dict, status=status.HTTP_200_OK)

    # 审批后的详情页
    @list_route(methods=['get'])
    def khk_retrieve(self, request):
        pk = request.GET.get('pk')
        queryset = CompanyInfo.objects.all().filter(transmitting_state=3).order_by('-transmitting_state')
        instance = queryset.filter(pk=pk)
        serializer = KHKCompanyInfoSerializer(instance, many=True)
        # 获取最近更新时间
        try:
            date_q1 = OperateLog.objects.filter(operationmodule="客户库", title=pk).order_by('-operationtime')[0].operationtime
        except Exception as e:
            date_q1 = 0
        try:
            date_q2 = RemarkEvolve.objects.filter(company=pk).order_by('-operationtime')[0].operationtime
        except Exception as e:
            date_q2 = 0
        update_date = compare_date(date_q1, date_q2)
        seri_data = serializer.data
        seri_data[0]["update_date"] = update_date
        data = seri_data[0]

        # 企业基本信息
        # company_info
        company_info = dict()
        company_info['company_name'] = data.pop('company_name')
        company_info['abbreviation'] = data.pop('abbreviation')
        company_info['company_url'] = data.pop('company_url')
        company_info['company_address'] = data.pop('company_address')
        if not company_info['company_address']:
            company_info['company_address'] = {
                "id": "",
                "province": "",
                "city": "",
                "detail": ""
            }
        company_info['industry'] = data.pop('industry')
        company_info['company_email'] = data.pop('company_email')
        company_info['GSZZ'] = data.pop('GSZZ')
        company_info['service_area'] = data.pop('service_area')
        company_info['platform_informatiom'] = data.pop('platform_informatiom')
        company_info['brand_effect'] = data.pop('brand_effect')
        company_info['customer_level'] = data.pop('customer_level')
        data['company_info'] = company_info
        company_info['customer_type'] = data.pop('customer_type')
        company_info['station_type'] = data.pop('station_type')
        # link_info
        link_info = data.get('link_info')
        if not link_info:
            for item in range(1, 5):
                link_dict = {
                    "id": "",
                    "linkman": "",
                    "link_phone": "",
                    "link_email": "",
                    "link_qq": "",
                    "link_work": ""
                }
                link_dict['link_type'] = item
                link_info.append(link_dict)

        # order_info
        order_info = data['order_info'] if data['order_info'] else {}

        visitor = data.pop('visitor')
        order_info['visitor'] = visitor

        consult = data.pop('consult')
        order_info['consult'] = consult

        training_method = data.pop('training_method')
        order_info['training_method'] = training_method

        special_selection = data.pop('special_selection')
        order_info['special_selection'] = special_selection

        sign_contract = data.pop('sign_contract')
        order_info['sign_contract'] = sign_contract

        kf_number = data.pop('kf_number')
        order_info['kf_number'] = kf_number

        cli_version = data.pop('cli_version')
        order_info['cli_version'] = cli_version

        order_info['transmitting_state'] = data.pop('transmitting_state')
        order_info['deploy_way'] = data.pop('deploy_way')
        order_info['classify'] = data.pop('classify')
        order_info['update_date'] = data.pop('update_date')
        # "id": ""
        if not order_info.get('id'):
            order_info['id'] = ""
        # "contract_start_time": ""
        if not order_info.get('contract_start_time'):
            order_info['contract_start_time'] = ""
        # "contract_end_time": ""
        if not order_info.get('contract_end_time'):
            order_info['contract_end_time'] = ""
        # "contract_index": ""
        if not order_info.get('contract_index'):
            order_info['contract_index'] = ""
        # "contract_accessory": ""
        if not order_info.get('contract_accessory') or order_info["contract_accessory"] == []:
            order_info['contract_accessory'] = ""
        else:
            order_info["contract_accessory"] = eval(order_info["contract_accessory"])
        # "contract_amount": ""
        if not order_info.get('contract_amount'):
            order_info['contract_amount'] = ""
        # "amount_cashed": ""
        if not order_info.get('amount_cashed'):
            order_info['amount_cashed'] = ""
        # "cashed_time": ""
        if not order_info.get('cashed_time'):
            order_info['cashed_time'] = ""
        # "created_at": ""
        if not order_info.get('created_at'):
            order_info['created_at'] = ""

        data['order_info'] = order_info
        # function_info
        contract_content = order_info.get('contract_content')
        if contract_content:
            order_info.pop('contract_content')
        data['function_info'] = contract_content
        # comment
        # sign_contract
        # id
        return Response(data)

    # 审批到开站（只有父站）
    @list_route(methods=['POST'])
    def approval_open(self, request):
        # 获取前端传过来的数据
        open_data = request.data

        func_list = open_data.get("func_list")
        account_conf_list = open_data['account_conf']

        common_open = CommonOpenSet()
        cmp_data = open_data['company_info']
        sta_data = open_data['station_info']
        #
        grid_sta = copy.deepcopy(sta_data)
        link_info_list = open_data['link_info']

        """
        公司信息
        """
        with transaction.atomic():
            # 获取公司实例，并对其信息进行修改
            company_info = CompanyInfo.objects.get(pk=cmp_data["id"])

            company_url_list = cmp_data.pop('company_url')
            company_address = cmp_data.pop('company_address')

            # 公司url
            common_open.open_url(company_info, company_url_list)
            # 公司地址
            common_open.open_address(company_info, company_address)
            # 公司其他信息
            company_info = common_open.open_company_some(cmp_data, company_info, sta_data)

            open_dict = {"online_status": False}

            open = OpenStationManage.objects.create(**open_dict)
            open.company_info = company_info

            """
            站点信息
            """
            station_info = common_open.open_create_station(open, sta_data)
            open.station_info = station_info
            open.save()
            """
            联系人信息
            """
            common_open.open_contact(company=company_info, link_info_list=link_info_list, method=0)
            """
            功能开关表信息
            """
            common_open.open_funclist(open, func_list)
            """
            账户信息
            """
            common_open.open_account(open, account_conf_list)
            # 服务组数据写入
            grid_id = grid_sta['grid']
            if int(open_data['station_info']['classify']) == 1:
                server_grp_name = SerGrpInquriesViewSet.min_sergrp_inquries(grid_id)
                server_grp = ServerGroup.objects.all().filter(group_name=server_grp_name).first()
                station_info.server_grp = server_grp
                station_info.save()
            company_info.transmitting_state = 0
            company_info.save()

        return Response({"info": "开通成功"}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # pk = kwargs["pk"]
        instance = self.get_object()
        # instance = CompanyInfo.objects.get(pk=pk)
        serializer = self.get_serializer(instance)
        data = dict(serializer.data)
        company_info = {}
        # 企业基本信息
        company_info['company_name'] = data.pop('company_name')
        company_info['abbreviation'] = data.pop('abbreviation')
        company_info['company_url'] = data.pop('company_url')
        company_info['company_address'] = data.pop('company_address')
        company_info['industry'] = data.pop('industry')
        company_info['company_email'] = data.pop('company_email')
        company_info['GSZZ'] = data.pop('GSZZ')
        company_info['service_area'] = data.pop('service_area')
        company_info['platform_informatiom'] = data.pop('platform_informatiom')
        company_info['brand_effect'] = data.pop('brand_effect')
        company_info['customer_level'] = data.pop('customer_level')
        data['company_info'] = company_info
        company_info['customer_type'] = data.pop('customer_type')
        company_info['station_type'] = data.pop('station_type')
        # 订单信息
        order_info = data['order_info'] if data['order_info'] else {}
        data['order_info'] = order_info
        if order_info:
            accessory = order_info.get('contract_accessory')
            if accessory:
                accessory = eval(accessory)
            order_info['contract_accessory'] = accessory

        visitor = data.get('visitor')
        if visitor:
            data.pop('visitor')
        order_info['visitor'] = visitor

        consult = data.get('consult')
        if consult:
            data.pop('consult')
        order_info['consult'] = consult

        training_method = data.get('training_method')
        if training_method:
            data.pop('training_method')
        order_info['training_method'] = training_method

        special_selection = data.get('special_selection')
        if special_selection:
            data.pop('special_selection')
        order_info['special_selection'] = special_selection

        sign_contract = data.get('sign_contract')
        if sign_contract:
            data.pop('sign_contract')
        order_info['sign_contract'] = sign_contract

        kf_number = data.get('kf_number')
        if kf_number:
            data.pop('kf_number')
        order_info['kf_number'] = kf_number

        cli_version = data.get('cli_version')
        if cli_version:
            data.pop('cli_version')
        order_info['cli_version'] = cli_version

        order_info['transmitting_state'] = data.pop('transmitting_state')
        order_info['deploy_way'] = data.pop('deploy_way')
        order_info['classify'] = data.pop('classify')
        # 功能信息
        contract_content = order_info.get('contract_content')
        if contract_content:
            order_info.pop('contract_content')
        data['function_info'] = contract_content
        # 联系人信息   不动

        return Response(data)

    def create(self, request, *args, **kwargs):
        # 是否已特批
        special_selection = request.data.get('order_info').get('special_selection')
        # 是否已签署合同
        sign_contract = request.data.get('order_info').get('sign_contract')
        # 是否已特批  如选择未签署，【是否已特批】字段需选择“是”，老客户请填“否”  默认为‘无’或者‘否’
        if (not sign_contract) and (not special_selection):
            return Response({'error': "未特批的非已签署合同"}, status=status.HTTP_400_BAD_REQUEST)
        result = request.data
        function_info = result.pop('function_info')
        company_info = result.pop('company_info')
        order_info = result.pop('order_info')
        result['visitor'] = order_info.pop('visitor')
        result['consult'] = order_info.pop('consult')
        result['training_method'] = order_info.pop('training_method')
        result['special_selection'] = order_info.pop('special_selection')
        result['sign_contract'] = order_info.pop('sign_contract')
        result['kf_number'] = order_info.pop('kf_number')
        result['cli_version'] = order_info.pop('cli_version')
        result['deploy_way'] = order_info.pop('deploy_way')
        result['classify'] = order_info.pop('classify')

        order_info['contract_content'] = function_info
        accessory = order_info.get('contract_accessory')
        try:
            accessory = json.dumps(accessory)
        except:
            pass
        order_info['contract_accessory'] = accessory
        result['order_info'] = order_info
        result.update(company_info)

        serializer = self.get_serializer(data=result)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                self.perform_create(serializer)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        result = request.data
        print('result===', type(result), result)
        # 是否已特批
        special_selection = result.get('order_info').get('special_selection')
        # 是否已签署合同
        sign_contract = result.get('order_info').get('sign_contract')
        # 是否已特批  如选择未签署，【是否已特批】字段需选择“是”，老客户请填“否”  默认为‘无’或者‘否’
        if (not sign_contract) and (not special_selection):
            return Response({'error': "未特批的非已签署合同"}, status=status.HTTP_400_BAD_REQUEST)
        # 前端传过来的 公司信息
        com_data = result.get("company_info")
        # 前端传过来的 订单信息
        ord_data = result.get("order_info")
        # 前端传过来的 联系人信息
        link_data_list = result.get("link_info")
        # 前端传过来的 模块信息
        func_data = result.get("function_info")

        common_open = CommonOpenSet()

        """
        公司信息相关修改
        """
        # 获取company_info实例
        company_info = CompanyInfo.objects.get(pk=result["id"])
        # 公司url
        common_open.open_url(company_info, com_data.get("company_url"))
        # 公司地址
        common_open.open_address(company_info, com_data.get("company_address"))

        company_info.company_name = com_data.get("company_name")
        company_info.abbreviation = com_data.get("abbreviation")
        company_info.company_email = com_data.get("company_email")
        company_info.industry = Industry.objects.get(industry=com_data.get("industry"))
        company_info.GSZZ = com_data.get("GSZZ")
        company_info.customer_type = com_data.get("customer_type")
        company_info.service_area = com_data.get("service_area")
        company_info.brand_effect = com_data.get("brand_effect")
        company_info.customer_level = com_data.get("customer_level")
        company_info.platform_informatiom = com_data.get("platform_informatiom")

        # 订单信息
        company_info.classify = ord_data.get("classify")
        company_info.cli_version = ord_data.get("cli_version")
        company_info.deploy_way = ord_data.get("deploy_way")
        company_info.kf_number = ord_data.get("kf_number")
        company_info.sign_contract = ord_data.get("sign_contract")
        company_info.special_selection = ord_data.get("special_selection")
        company_info.training_method = ord_data.get("training_method")
        company_info.visitor = ord_data.get("visitor")
        company_info.consult = ord_data.get("consult")

        company_info.save()

        """
        修改联系人信息
        """
        common_open.open_contact(company_info,link_data_list,0)

        """
        订单信息修改
        """
        # 获取订单信息实例
        order_info = OrderManage.objects.get(pk=ord_data["id"])

        order_info.contract_amount = ord_data.get("contract_amount")
        order_info.amount_cashed = ord_data.get("amount_cashed")
        order_info.contract_start_time = ord_data.get("contract_start_time")
        order_info.contract_end_time = ord_data.get("contract_end_time")
        order_info.contract_index = ord_data.get("contract_index")
        accessory = ord_data.get('contract_accessory')
        try:
            accessory = json.dumps(accessory)
        except:
            pass
        order_info.contract_accessory = accessory
        order_info.contract_content = func_data
        order_info.save()
        return Response({"info": "修改成功"}, status=status.HTTP_200_OK)


class OrderManageSet(viewsets.ModelViewSet):
    queryset = OrderManage.objects.all().order_by("-id")
    serializer_class = OrderManageSerializer


class StationInfoSet(viewsets.ModelViewSet):
    queryset = StationInfo.objects.all().order_by("-id")
    serializer_class = StationInfoSerializer


class IndustrySet(viewsets.ModelViewSet):
    queryset = Industry.objects.all().order_by('-id')
    serializer_class = IndustrySerializer
    pagination_class = None


class AreaInfoSet(viewsets.ModelViewSet):
    queryset = AreaInfo.objects.all().order_by('-id')
    serializer_class = AreaInfoSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = AreaInfo.objects.all().order_by('-id')
        level = self.request.GET.get('level', "").strip()  # 是什么级别的：省或市
        province = self.request.GET.get('province', "").strip()

        if level:  # 查询所有省, level为1
            if level == '1':
                queryset = queryset.filter(aPArea__isnull=True)
        if province:  # 查询某省所有城市
            queryset = queryset.filter(aPArea__id=province)

        return queryset


@api_view(['GET'])
def customer_oper_type(request):
    fields = ['id', 'name']
    ret = {'data': []}
    for item in OPERATE_ACTION_CHOICES:
        ret['data'].append(dict(zip(fields, item)))
    return Response(ret, status=status.HTTP_200_OK)


# 开站导出数据清洗
def data_cleaning(new_result):
    if new_result.get('station_info__cli_version') == 1:
        new_result['station_info__cli_version'] = 'B2B'
    if new_result.get('station_info__cli_version') == 2:
        new_result['station_info__cli_version'] = 'B2C'
    if new_result.get('station_info__cli_version') == 3:
        new_result['station_info__cli_version'] = '不限'
    if new_result.get('station_info__cli_version') == 4:
        new_result['station_info__cli_version'] = 'B2B2C'

    if new_result.get('station_info__deploy_way') == 1:
        new_result['station_info__deploy_way'] = '标准版'
    if new_result.get('station_info__deploy_way') == 2:
        new_result['station_info__deploy_way'] = '公有云'
    if new_result.get('station_info__deploy_way') == 3:
        new_result['station_info__deploy_way'] = '专属云'
    if new_result.get('station_info__deploy_way') == 4:
        new_result['station_info__deploy_way'] = '私有云'

    if new_result.get('company_info__station_type') == 1:
        new_result['company_info__station_type'] = '试用客户'
    if new_result.get('company_info__station_type') == 2:
        new_result['company_info__station_type'] = '正式客户'
    if new_result.get('company_info__station_type') == 3:
        new_result['company_info__station_type'] = '市场渠道客户'
    if new_result.get('company_info__station_type') == 4:
        new_result['company_info__station_type'] = '商务渠道客户'
    if new_result.get('company_info__station_type') == 5:
        new_result['company_info__station_type'] = '自用站点'

    if new_result.get('online_status') == 1:
        new_result['online_status'] = dict(STATUS_TYPES)[True]
    if new_result.get('online_status') == 0:
        new_result['online_status'] = dict(STATUS_TYPES)[False]

    if new_result.get('station_info__classify') == 1:
        new_result['station_info__classify'] = dict(PROD_SERV_VERSIONS)[True]
    if new_result.get('station_info__classify') == 2:
        new_result['station_info__classify'] = dict(PROD_SERV_VERSIONS)[2]

    return new_result


# 以站点为维度 反向同步站点（重构和经典）
@api_view(['GET'])
def update_site_open_station(request):
    site_id = request.GET.get('site_id', '')
    if not site_id:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '缺少站点参数'})
    classify = OpenStationManage.objects.all().filter(station_info__company_id=site_id)\
        .select_related('station_info__classify').values_list('station_info__classify', flat=True)

    if classify[0] == 1:
        info = ForSiteSynchronous(site_id)
        base_info = BaseStart(info.grid_name, info.site_ids)
        base_info.start()
        Command(site_id=site_id).handle()
    else:
        station_data = StationData()
        # 这个site不是一个siteid 而是包含siteid信息的字典
        for site in station_data.station_list:
            if site_id == site.get('siteid'):
                func_list = station_data.get_info(site)
                station_info = station_data.get_parse_info(site)
                station_info['func_data'] = func_list
                site_manager = RefactorStation(station_info)
                result = site_manager.start()
    return Response(status=status.HTTP_200_OK, data='for_site_id end')


# 同步站点行业信息
@api_view(['POST'])
def syn_station_industry(request):
    try:
        # myFile = request.FILES["file"]  # 获取上传的文件，如果没有文件，则默认为None
        # if not myFile:
        #     return Response({"error": "没有文件上传"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # file = myFile.read()
        # data = syn_industry(file_contents=file)
        params = request.body.decode('utf-8')
        data = json.loads(params)
        assert isinstance(data, list)
        with transaction.atomic():
            for item in data:
                site_id = item.get('siteid')
                industry_name = item.get('industry')
                industry_ins = Industry.objects.all().filter(industry=industry_name).first()

                if industry_ins:
                    company_ins = CompanyInfo.objects.all().filter(open_station__station_info__company_id=site_id).first()
                    if company_ins:
                        company_ins.industry=industry_ins
                        company_ins.save()
                    else:
                        print('error', site_id)
                        continue

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


# 同步 cli_version字段到companyInfo 表  等
@api_view(['GET'])
def update_cli_version(request):
    # 客户版本同步
    data = CompanyInfo.objects.all()\
        .select_related('open_station__station_info__cli_version',
                        'open_station__station_info__deploy_way',
                        'open_station__station_info__classify')\
        .values_list('open_station__station_info__cli_version',
                     'open_station__station_info__deploy_way',
                     'open_station__station_info__classify', 'id')
    try:
        with transaction.atomic():
            i = 0
            for item in data:
                company_info = CompanyInfo.objects.all().get(pk=item[3])
                company_info.cli_version = item[0]
                company_info.deploy_way = item[1]
                company_info.classify = item[2]
                company_info.save()
                print(i)
                i += 1
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # 联系人同步
    link_data = ContactInfo.objects.all().select_related('station__company_info') \
        .values_list('station', 'id')
    try:
        with transaction.atomic():
            i = 0
            for item in link_data:
                link_info = ContactInfo.objects.all().get(pk=item[1])
                link_info.company = CompanyInfo.objects.all().filter(pk=item[0]).first()
                link_info.save()
                print(i)
                i += 1
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)


def transmitting_state():
    """
    流转状态的修改（初始化oa旧站点数据的流转状态为0 审核通过）
    因为流转状态为新增字段 默认值为未审核 故修改旧数据的流转状态为审核通过
    """
    status = CompanyInfo.objects.all().update(transmitting_state=0)
    return 'end'

def online_change():
    """
    开通状态的站点 company_info表里的审批状态变更1 再执行 (online_status=False,transmitting_state=0)
    :return:
    """
    open_set = OpenStationManage.objects.filter(online_status=True)
    for open in open_set:
        ret = CompanyInfo.objects.filter(open_station__id=open.id).update(transmitting_state=3)
    return 'ok'