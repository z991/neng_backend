from django.db import transaction
from applications.workorder_manage.models import OpenStationManage, CompanyInfo, \
    StationInfo, CompanyAddress, CompanyUrl, ContactInfo, AccountConf
from applications.production_manage.models import Grid
from libs.push_service_cg.push_service import Push_manage
class CopyLogic:

    def copy_logic(self,grid,company_id,id):
        try:
            #grid = 1
            # 企业id
            #company_id = 'kf_111'
            # id
            #id = '复制站点的id'
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
                    "classify": station_info.classify,
                    "deploy_way": station_info.deploy_way,
                    "open_station_time": station_info.open_station_time,
                    "close_station_time": station_info.close_station_time,
                    "sales": station_info.sales,
                    "pre_sales": station_info.pre_sales,
                    "oper_cslt": station_info.oper_cslt,
                    "impl_cslt": station_info.impl_cslt,
                    "oper_supt": station_info.oper_supt,
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
                return True
        except Exception as e:
            print(e)
            return False
    def run(self):
        #节点id
        grid = 1
        #需复制的站点id
        company_id = ''
        #被复制的站点id
        id = 8
        for siteid in range(88100000,88101000):
            company_id = 'kf_'+str(siteid)
            print(company_id)
            self.copy_logic(grid,company_id,id)
            Push_manage(company_id, 'jdtest', True).push_data()
            print('----end----')
