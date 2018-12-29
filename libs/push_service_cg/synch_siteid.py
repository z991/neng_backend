import time
from applications.workorder_manage.models import CompanyInfo, StationInfo, Industry, OpenStationManage,\
    ContactInfo, CompanyUrl, AccountConf, CompanyAddress, AreaInfo
from applications.production_manage.models import Grid, SingleSelection, Product, FunctionInfo,\
    DataBaseInfo, ServerGroup
import requests
from applications.data_manage.models import InquiriesData
from ldap_server.configs import CUSTOM_OLD, CLI_B2C, CLI_B2B, STATION_OFFICAL, STATION_TRIAL
from applications.production_manage.models import Grid, SingleSelection, Product, FunctionInfo,\
    DataBaseInfo, ServerGroup
from applications.workorder_manage.models import CompanyInfo, StationInfo, Industry, OpenStationManage,\
    ContactInfo, CompanyUrl, AccountConf, CompanyAddress, AreaInfo
from urllib import parse
from libs.hash import decrypt
from libs.datetimes import timestamp_to_date
from django.db import transaction, DatabaseError
from libs.mysql_helper import Connection, ObjDict
from ldap_server.configs import VERSION_ID
from libs.classic_service.classic_model import *
from libs.basemodel import BaseModelHelp
class SynchSiteid:
    """
    站点从重构同步到运营平台，已存在的跳过
    """
    def synch_siteid(self):
        all_siteid_url = "https://bj-v4-n1-gateway.ntalker.com/usercenter/enterprise"
        resp = requests.get(url=all_siteid_url, timeout=10)
        siteids = resp.json()
        for key in list(siteids['data']):
            siteid = key['siteid']
            queryset = StationInfo.objects.filter(company_id=siteid)
            if queryset:
                continue
            print(siteid)
            name = key['name']
            siteid_url = "https://bj-v4-n1-gateway.ntalker.com/usercenter/usercenter/enterprise/productPoint?siteid="+siteid
            resp = requests.get(url=siteid_url, timeout=10)
            functions = resp.json()
            dict_tmp = {}
            for k in list(functions['data']):
                func_code = k['productPointid']
                func_value = k['isSwitch']
                tmp = {func_code:func_value}
                dict_tmp.update(tmp)
            result = ObjDict(company_data=self.parse_company_data(siteid,name),
                                func_data=dict_tmp)
            site_manager = SiteManager(result)
            site_manager.start()
            print('end')
    def get_cli_version(self,site_id: str):
        """判断site_id的版本"""
        start, end = site_id.split("_")
        if start == "kf":
            return CLI_B2C
        elif start != "kf" and end == "1000":
            return CLI_B2B
        else:
            print(11111)
    def get_classify(self,classify):
        """获取行业信息, 如果源数据不存在则返回其他行业"""
        if not classify:
            return Industry.objects.get(industry="其他")
        industry, _ = Industry.objects.get_or_create(industry=classify)
        return industry
    def parse_company_data(self, siteid,name):
        self.grid = Grid.objects.all().get(grid_name='cg-bj')
        return ObjDict(
            online_status=1,
            # company_info
            station_type=2,  # 站点类型
            company_name=name,  # 公司名称
            company_email=1,  # 公司邮
            industry=self.get_classify(''),  # 行业
            GSZZ='0',  # 营业执照
            customer_type=True,  # 客户信息
            service_area='0',  # 服务地区
            # station_info
            company_id=siteid,  # 站点id
            deploy_way=1,  # 部署信息
            validity_days=364,  # 有效期
            grid_name=self.grid,  # 节点名称
            cli_version=self.get_cli_version(siteid),  # 客户版本 b2b b2c
            # pact_products=Product.objects.all(),  # 绑定产品
            open_station_time=timestamp_to_date('1545706251000'),  # 开站时间
            close_station_time=timestamp_to_date('1577242251000'),  # 到期时间
            version_id=1,  # version_id : grid
            sales='0',  # 销售人员
            pre_sales='0',  # 售前人员
            oper_cslt='0',  # 运营顾问
            impl_cslt='0',  # 实施顾问
            oper_supt='0',  # 运营支持
            # contact_info 联系人信息 电话 邮箱 qq
            link_man='0',
            link_phone='0',
            link_email='0',
            link_qq='0',
            # company_address
            province='',
            city='',
            address='',
            oa_address='',
            # company_url 企业网址
            company_url='0',
            # account_conf 账户信息
            user_name='admin',
            set_pwd='111111',
            # 服务组
            real_grid_name=''
        )

class SiteManager(object):
    """
    功能： 实施创建或修改一个站点
    params: 创建站点全部信息，包括企业信息，站点信息，账户信息，产品信息及功能开关
    """
    def __init__(self, data):
        self.company_data = data.company_data
        self.func_data = data.func_data
        self.site_id = data.company_data.company_id

    # 创建公司信息
    def create_company_info(self, company_address):
        company_info, _ = CompanyInfo.objects.update_or_create(
            defaults=dict(station_type=self.company_data.station_type,
                          company_name=self.company_data.company_name,
                          abbreviation=self.company_data.company_name,
                          company_address=company_address,
                          cli_version=self.company_data.cli_version,
                          company_email=self.company_data.company_email,
                          industry=self.company_data.industry,
                          GSZZ=self.company_data.GSZZ,
                          customer_type=self.company_data.customer_type,
                          service_area=self.company_data.service_area),
            open_station__station_info__company_id=self.site_id,
        )
        return company_info

    # 创建站点信息
    def create_station_info(self):

        grid = Grid.objects.filter(grid_name=self.company_data.grid_name.grid_name).first()
        if not grid:
            raise DatabaseError(f"{self.company_data.company_id}未找到对应节点{self.company_data.grid_name.grid_name}")

        station_info, _ = StationInfo.objects.update_or_create(
            defaults=dict(deploy_way=self.company_data.deploy_way,
                          validity_days=self.company_data.validity_days,
                          grid=grid,
                          cli_version=self.company_data.cli_version,
                          open_station_time=self.company_data.open_station_time,
                          close_station_time=self.company_data.close_station_time,
                          version_id=self.company_data.version_id,
                          sales=self.company_data.sales,
                          classify=2,
                          pre_sales=self.company_data.pre_sales,
                          oper_cslt=self.company_data.oper_cslt,
                          impl_cslt=self.company_data.impl_cslt,
                          oper_supt=self.company_data.oper_supt, ),
            company_id=self.company_data.company_id,
        )
        return station_info

    # 创建公司地址信息
    def create_company_address(self):
        province = AreaInfo.objects.filter(atitle=self.company_data.province).first()
        city = AreaInfo.objects.filter(atitle=self.company_data.city).first()
        if not (city and province):
            return None
        company_address, _ = CompanyAddress.objects.update_or_create(
            defaults=dict(province=province,
                          city=city,
                          detail=self.company_data.address),
            company_info__open_station__station_info__company_id=self.site_id)
        return company_address

    # 创建一个开站信息
    def create_open_station(self, company_info, station_info, online_status):
        if checkversion(self.site_id) == 'b2b2c':
            siteid_b2b = self.site_id.split('_')[0]+'_1000'
            its_parent_id = OpenStationManage.objects.filter(station_info__company_id=siteid_b2b).values("id")[0]['id']
            open_station, _ = OpenStationManage.objects.update_or_create(
                defaults=dict(online_status=online_status,
                              company_info=company_info,
                              station_info=station_info,
                              its_parent_id=its_parent_id),
                station_info__company_id=self.site_id,
            )
        else:
            open_station, _ = OpenStationManage.objects.update_or_create(
                defaults=dict(online_status=online_status,
                              company_info=company_info,
                              station_info=station_info, ),
                station_info__company_id=self.site_id,
            )
        return open_station

    # 创建联系人信息
    def create_contact_info(self, open_station):
        if self.company_data.link_man or self.company_data.link_phone or self.company_data.link_email \
                or self.company_data.link_qq:
            contact_info = ContactInfo.objects.update_or_create(
                station=open_station,
                linkman=self.company_data.link_man,
                link_phone=self.company_data.link_phone,
                link_email=self.company_data.link_email,
                link_qq=self.company_data.link_qq
            )
            return contact_info

    # 创建企业网址
    def create_company_url(self, company_info):
        CompanyUrl.objects.filter(company_info__open_station__station_info__company_id=self.site_id).delete()
        if self.company_data.company_url:
            CompanyUrl.objects.create(
                company_url=self.company_data.company_url,
                company_info=company_info
            )

    # 创建账户信息
    def create_account_conf(self, open_station):
        AccountConf.objects.filter(station__station_info__company_id=self.site_id).delete()
        AccountConf.objects.create(
            user_name=self.company_data.user_name,
            set_pwd=self.company_data.set_pwd,
            station=open_station,
        )

    # 创建功能开关信息
    def create_func_list(self, open_station: OpenStationManage):
        objs = set()
        for func_code, value in self.func_data.items():
            # 选择
            selection = SingleSelection.objects.filter(function__func_code=func_code, select_value=value).first()
            if func_code not in ('kfsum', 'contime', 'ticket'):
                value = 0 if value is None else value
                slc = SingleSelection.objects.filter(select_value=value, function__func_code=func_code).first()
                if slc:
                    objs.add(slc)
            # 工单处理
            elif func_code == 'ticket':
                if value == 0:
                    slc = SingleSelection.objects.filter(select_value=0, function__func_code='ticket').first()
                    if slc:
                        objs.add(slc)
                    new_slc = SingleSelection.objects.filter(select_value=0, function__func_code='new_ticket').first()
                    if slc:
                        objs.add(new_slc)
                # 老工单
                elif value == 1:
                    slc = SingleSelection.objects.filter(select_value=1, function__func_code='ticket').first()
                    if slc:
                        objs.add(slc)
                # 新工单
                elif value == 2:
                    slc = SingleSelection.objects.filter(select_value=1, function__func_code='new_ticket').first()
                    if slc:
                        objs.add(slc)

            # 文本框
            elif func_code == "kfsum":
                func = FunctionInfo.objects.all().get(func_code="kfsum")
                SingleSelection.objects.filter(function=func, station__station_info__company_id=self.site_id).hard_delete()
                selection = SingleSelection.objects.create(function=func, select_name=value,
                                                           select_value=value)
                objs.add(selection)
            elif func_code == "contime":
                func = FunctionInfo.objects.all().get(func_code="contime")
                SingleSelection.objects.filter(function=func, station__station_info__company_id=self.site_id).hard_delete()
                selection = SingleSelection.objects.create(function=func, select_name=value,
                                                           select_value=value)
                objs.add(selection)

        open_station.func_list.set(objs=objs)

    def start(self):
        try:
            with transaction.atomic():
                company_address = self.create_company_address()
                company_info = self.create_company_info(company_address)
                station_info = self.create_station_info()
                self.create_pact_product(station_info)
                open_station = self.create_open_station(company_info, station_info, self.company_data.online_status)
                self.create_company_url(company_info)
                self.create_account_conf(open_station)
                self.create_func_list(open_station)
                self.create_contact_info(open_station)

        except DatabaseError as e:
            print(e)

    # 关联产品与站点
    def create_pact_product(self, station_info):
        for func_code, value in self.func_data.items():
            if value:
                products = Product.objects.all().filter(function__func_code=func_code).first()
                if products:
                    station_info.pact_products.add(products)


