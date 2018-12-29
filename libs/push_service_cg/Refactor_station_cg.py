import requests
import datetime
import logging

from django.db import transaction, DatabaseError
from libs.datetimes import datetime_delta
from ldap_server.configs import CLI_B2C, CLI_B2B, VERSION_ID
from applications.production_manage.models import Grid, SingleSelection, Product, FunctionInfo,\
    DataBaseInfo, ServerGroup
from applications.workorder_manage.models import CompanyInfo, StationInfo, Industry, OpenStationManage,\
    ContactInfo, CompanyUrl, AccountConf, CompanyAddress, AreaInfo

logger = logging.getLogger('django')


class StationData(object):
    def __init__(self):
        self.grid = self.get_grid()
        self.region_info = self.get_region_info()
        self.station_list = self.get_company_list()

    def get_grid(self):
        data = []
        res = Grid.objects.all().filter(version_type=2).values('id', 'domain_name')
        for each in res:
            usercenter = eval(each['domain_name']).get('usercenter')
            dolphinsetting = eval(each['domain_name']).get('dolphinsetting')
            if usercenter.startswith('http'):
                data.append({'grid': each['id'], 'usercenter': usercenter,
                             'dolphin': dolphinsetting})
        return data

    # 获取地域信息
    def get_region_info(self):
        data = []
        for each in self.grid:
            url = each.get('dolphin') + '/region/'
            result = requests.get(url=url)
            data.extend(result.json())
        return data

    # 获取企业信息和站点列表
    def get_company_list(self):
        data = []
        for item in self.grid:
            url = item.get('usercenter') + '/enterprise/'
            grid_id = item.get('grid')
            usercenter = item.get('usercenter')
            dolphin = item.get('dolphin')
            result = requests.get(url=url)
            company_info = result.json()
            for each in company_info.get('data', []):
                each['grid_id'] = grid_id
                each['usercenter'] = usercenter
                each['dolphin'] = dolphin
                data.append(each)
        return data

    # 获取功能开关信息（单个站点）返回列表
    def get_info(self, site):
        function_url = site.get('usercenter') + '/usercenter/enterprise/productPoint/'
        siteid = site.get('siteid')
        url = function_url + '?siteid=%s' % siteid
        res = requests.get(url=url)
        result = res.json()
        ins = []
        for each in result['data']:
            select = each['isSwitch']
            site_id = each['siteid']
            function = each['productPointname']
            product = each['classifyname']
            if site_id != siteid:
                return {'error': site_id + '!=' + siteid}
            ins.append({'site_id': site_id,
                        'product': product,
                        'function': function,
                        'select': select,
                        'parent_func': ''})
            child_function = each['enterpriseProductPoints']
            for item in child_function:
                inner_select = item['isSwitch']
                inner_site_id = item['siteid']
                inner_function = item['productPointname']
                inner_product = item['classifyname']
                ins.append({'site_id': inner_site_id,
                            'product': inner_product,
                            'function': inner_function,
                            'select': inner_select,
                            'parent_func': function})

        return ins

    # 获取功能开关信息（线上所有站点） 遍历 返回字典
    def get_function_info(self):
        data = {}
        for site in self.station_list:
            data[site.get('siteid')] = self.get_info(site)
        return data

    # 解析企业信息 返回对象
    def get_parse_info(self, each):
        instance = {}
        instance['site_id'] = each['siteid']
        query = OpenStationManage.objects.all().filter(station_info__classify=2) \
            .filter(station_info__company_id=each['siteid']) \
            .select_related('company_info__company_email', 'company_info__service_area', 'station_info__sales',
                            'station_info__pre_sales', 'station_info__oper_cslt', 'station_info__impl_cslt',
                            'station_info__oper_supt', 'company_info__company_address',
                            'link_info__linkman', 'link_info__link_phone', 'link_info__link_email',
                            'link_info__link_qq', 'company_info__GSZZ') \
            .values_list('company_info__company_email', 'company_info__service_area', 'station_info__sales',
                         'station_info__pre_sales', 'station_info__oper_cslt', 'station_info__impl_cslt',
                         'station_info__oper_supt', 'company_info__company_address', 'link_info__linkman',
                         'link_info__link_phone', 'link_info__link_email', 'link_info__link_qq',
                         'company_info__GSZZ')

        if not query:
            query = [('0', '0', '0', '0', '0', '0', '0', 54, '0', '0', '0', '0', '0')]
        email, service_area, sales, pre_sales, oper_cslt, impl_cslt, oper_supt, addr, \
        linkman, linkphone, linkemail, linkqq, gszz = query[0]
        # 销售人员
        instance['sales'] = sales
        # 售前人员
        instance['pre_sales'] = pre_sales
        # 运营顾问
        instance['oper_cslt'] = oper_cslt
        # 实施顾问
        instance['impl_cslt'] = impl_cslt
        # 运营支持
        instance['oper_supt'] = oper_supt

        instance['link_man'] = linkman
        instance['link_phone'] = linkphone
        instance['link_email'] = linkemail
        instance['link_qq'] = linkqq

        instance['grid_id'] = each['grid_id']
        instance['online_status'] = each['enabled']
        # 站点类型
        instance['station_type'] = each.get('type') if each.get('type') else 2
        # 公司名称
        instance['company_name'] = each['name']
        # 公司简称
        instance['abbreviation'] = each['name']
        # 公司邮箱
        instance['company_email'] = each.get('email') if each.get('email') else email
        # 【外键】 所属行业
        instance['industry'] = each.get('industry') if each.get('industry') else '0'
        # 营业执照名称
        instance['GSZZ'] = each.get('GSZZ') if each.get('GSZZ') else gszz
        # 客户性质 布尔：(0,新客户) / (1,老客户信息补录) / 必填
        instance['customer_type'] = each.get('customer_type') if each.get('customer_type') else 0
        # 客服工作区域
        instance['service_area'] = each.get('service_area') if each.get('service_area') else 1
        # 联系电话
        instance['link_phone'] = each.get('phone') if each.get('phone') else ''
        # 公司地址 对象  必填
        instance['street'] = each.get('street') if each.get('street') else ''
        country = each.get('country') if each.get('country') else ''
        province = each.get('province') if each.get('province') else ''
        city = each.get('city') if each.get('city') else ''
        if not (city and province and country and instance['street']):
            instance['oa_address'] = addr
        for item in self.region_info:
            if item.get('id') == country:
                instance['country'] = item.get('name', '')
            elif item.get('id') == province:
                instance['province'] = item.get('name', '')
            elif item.get('id') == city:
                instance['city'] = item.get('name', '')
            elif instance.get('country') and instance.get('province') and instance.get('city'):
                break
        return instance

    # 解析企业信息遍历 返回列表
    def parse_company(self):
        data = []
        for each in self.station_list:
            data.append(self.get_parse_info(each))
        return data


# 重构数据写入
class RefactorStation(object):
    def __init__(self, data):
        self.company_data = data
        self.func_data = data.get('func_data')
        self.site_id = data.get('site_id')

    @staticmethod
    def get_cli_version(site_id: str):
        """判断site_id的版本"""
        start, end = site_id.split("_")
        if start == "kf":
            return CLI_B2C
        elif start != "kf" and end == "1000":
            return CLI_B2B

    def create_company_info(self, company_address):
        industry, _ = Industry.objects.get_or_create(industry=self.company_data.get('industry'))
        company_info, _ = CompanyInfo.objects.update_or_create(
            defaults=dict(station_type=self.company_data.get('station_type'),
                          company_name=self.company_data.get('company_name'),
                          abbreviation=self.company_data.get('abbreviation'),
                          company_address=company_address,
                          company_email=self.company_data.get('company_email'),
                          industry=industry,
                          cli_version=self.get_cli_version(self.company_data['site_id']),
                          GSZZ=self.company_data.get('GSZZ'),
                          customer_type=self.company_data.get('customer_type'),
                          service_area=self.company_data.get('service_area')),
            open_station__station_info__company_id=self.site_id,
        )
        return company_info

    def create_station_info(self):
        grid = Grid.objects.filter(pk=self.company_data.get('grid_id')).first()
        if not grid:
            logger.error(f"{self.company_data.get('site_id')}未找到对应节点id{self.company_data.get('grid_id')}")
            raise DatabaseError(f"{self.company_data.get('site_id')}未找到对应节点id{self.company_data.get('grid_id')}")
        # 部署方式
        deploy_way = self.company_data.get('deploy_way', 1)
        # 有效期
        validity_days = self.company_data.get('validity_days', 365)
        # 客户版本
        cli_version = self.get_cli_version(self.company_data['site_id'])
        # 开站日期
        open_station_time = datetime.date.today()
        # 到期日期
        close_station_time = datetime_delta(open_station_time, days=365)
        # 销售人员
        sales = self.company_data.get('sales', '0')
        # 售前人员
        pre_sales = self.company_data.get('pre_sales', '0')
        # 运营顾问
        oper_cslt = self.company_data.get('oper_cslt', '0')
        # 实施顾问
        impl_cslt = self.company_data.get('impl_cslt', '0')
        # 运营支持
        oper_supt = self.company_data.get('oper_supt', '0')
        station_info, _ = StationInfo.objects.update_or_create(
            defaults=dict(deploy_way=deploy_way,
                          validity_days=validity_days,
                          grid=grid,
                          cli_version=cli_version,
                          open_station_time=open_station_time,
                          close_station_time=close_station_time,
                          sales=sales,
                          classify=2,
                          pre_sales=pre_sales,
                          oper_cslt=oper_cslt,
                          impl_cslt=impl_cslt,
                          oper_supt=oper_supt, ),
            company_id=self.company_data.get('site_id'),
        )
        return station_info

    def create_company_address(self):
        if self.company_data.get('oa_address'):
            return CompanyAddress.objects.all().get(pk=self.company_data.get('oa_address'))
        province_value = self.company_data.get('province') if self.company_data.get('province') else ''
        city_value = self.company_data.get('city') if self.company_data.get('city') else ''
        detail_value = self.company_data.get('street')

        province = AreaInfo.objects.filter(atitle=province_value).first()
        city = AreaInfo.objects.filter(atitle=city_value).first()
        # 传过来数据没有province和city 或者没有找到province和city 返回None
        if not (city and province):
            return None
        company_address, _ = CompanyAddress.objects.update_or_create(
            defaults=dict(province=province,
                          city=city,
                          detail=detail_value),
            company_info__open_station__station_info__company_id=self.site_id)
        return company_address

    def create_contact_info(self, open_station):
        if self.company_data.get('link_man') or self.company_data.get('link_phone')\
                or self.company_data.get('link_email') or self.company_data.get('link_qq'):
            contact_info = ContactInfo.objects.update_or_create(
                station=open_station,
                linkman=self.company_data.get('link_man'),
                link_phone=self.company_data.get('link_phone'),
                link_email=self.company_data.get('link_email'),
                link_qq=self.company_data.get('link_qq')
            )
            return contact_info

    def create_company_url(self, company_info):
        if self.company_data.get('company_url'):
            CompanyUrl.objects.filter(company_info__open_station__station_info__company_id=self.site_id).delete()
            if self.company_data.company_url:
                CompanyUrl.objects.create(
                    company_url=self.company_data.get('company_url'),
                    company_info=company_info
                )

    def create_account_conf(self, open_station):
        if self.company_data.get('user_name') and self.company_data.get('set_pwd'):
            AccountConf.objects.filter(station__station_info__company_id=self.site_id).delete()
            AccountConf.objects.create(
                user_name=self.company_data.get('user_name'),
                set_pwd=self.company_data.get('set_pwd'),
                station=open_station,
            )
        else:
            AccountConf.objects.create(
                user_name='admin',
                set_pwd='111111',
                station=open_station,
            )

    def create_open_station(self, company_info, station_info):
        online_status = self.company_data.get('online_status')
        objs = set()
        for item in self.func_data:
            func_name = item.get('function')
            select_value = item.get('select')
            product = item.get('product')
            # 找到功能开关实例
            slc = SingleSelection.objects.all().filter(select_value=select_value,
                                                       function__func_name=func_name,
                                                       function__product__product=product).first()
            if slc:
                objs.add(slc.id)

        open_station, _ = OpenStationManage.objects.update_or_create(
            defaults=dict(online_status=online_status,
                          company_info=company_info,
                          station_info=station_info,
                          ),
            station_info__company_id=self.site_id,
        )
        return open_station

    def create_pact_product(self, station_info):
        pro_list = []
        for item in self.func_data:
            product = item.get('product')
            if product not in pro_list:
                pro_list.append(product)
        products = Product.objects.all().filter(product__in=pro_list)
        station_info.pact_products.set(products)

    def create_func_list(self, open_station: OpenStationManage):
        objs = set()
        for item in self.func_data:
            function = item.get('function')
            select_value = item.get('select')
            # 选择
            selection = SingleSelection.objects.filter(function__func_name=function,
                                                       select_value=select_value).first()
            if selection:
                objs.add(selection)

        open_station.func_list.set(objs=objs)

    def update_contact_info(self, open_station):
        if self.company_data.get('link_man') or self.company_data.get('link_phone')\
                or self.company_data.get('link_email') or self.company_data.get('link_qq'):
            contact_info = ContactInfo.objects.update_or_create(
                station=open_station,
                linkman=self.company_data.get('link_man'),
                link_phone=self.company_data.get('link_phone'),
                link_email=self.company_data.get('link_email'),
                link_qq=self.company_data.get('link_qq')
            )
            return contact_info

    def start(self):
        try:
            with transaction.atomic():
                company_address = self.create_company_address()
                company_info = self.create_company_info(company_address)
                station_info = self.create_station_info()
                # 增加合同产品
                self.create_pact_product(station_info)
                print(company_info, station_info)
                # 站点新增
                open_station = self.create_open_station(company_info, station_info)

                # # 增加企业地址
                self.create_company_url(company_info)
                # 增加账号信息
                self.create_account_conf(open_station)
                # 增加功能开关信息
                self.create_func_list(open_station)
                # 增加联系人信息
                self.create_contact_info(open_station)

                return 'company_name: %s, station_name: %s' %(company_info, station_info)

        except DatabaseError as e:
            logger.error(
                f"error occurred when storing {self.company_data.get('company_id')}\nerror info: {e}\n"
                f"current variables:\n{self.company_data}\n{self.func_data}\n")
            return 'error'


def start():
    station_data = StationData()
    func_list = station_data.get_function_info()
    company_info = station_data.parse_company()
    for site in company_info:
        print(site)
        site_id = site.get('site_id')
        site['func_data'] = func_list.get(site_id)
        print(func_list.get(site_id))
        site_manager = RefactorStation(site)
        result = site_manager.start()
        print(result)
