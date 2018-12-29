import datetime
import logging

from django.core.management.base import BaseCommand
from django.db import transaction, DatabaseError

from applications.production_manage.models import Grid, SingleSelection, Product, FunctionInfo
from applications.workorder_manage.models import CompanyInfo, StationInfo, Industry, OpenStationManage, ContactInfo, \
    CompanyUrl, AccountConf, CompanyAddress, AreaInfo
from ldap_server.configs import CUSTOM_OLD, CLI_B2C, CLI_B2B, STATION_OFFICAL, STATION_TRIAL
from libs.datetimes import timestamp_to_date
from libs.hash import decrypt
from libs.mysql_helper import Connection, ObjDict

logger = logging.getLogger(__name__)


class SiteManager(object):
    def __init__(self, data):
        self.company_data = data.company_data
        self.func_data = data.func_data
        self.site_id = data.company_data.company_id

    def create_company_info(self, company_address):
        company_info, _ = CompanyInfo.objects.update_or_create(
            defaults=dict(station_type=self.company_data.station_type,
                          company_name=self.company_data.company_name,
                          abbreviation=self.company_data.company_name,
                          company_address=company_address,
                          company_email=self.company_data.company_email,
                          industry=self.company_data.industry,
                          GSZZ=self.company_data.GSZZ,
                          customer_type=self.company_data.customer_type,
                          service_area=self.company_data.service_area),
            open_station__station_info__company_id=self.site_id,
        )
        return company_info

    def create_station_info(self):
        grid = Grid.objects.filter(grid_name=self.company_data.grid_name.grid_name).first()
        if not grid:
            logger.error(f"{self.company_data.company_id}未找到对应节点{grid_name}")
            raise DatabaseError(f"{self.company_data.company_id}未找到对应节点{grid_name}")
        station_info, _ = StationInfo.objects.update_or_create(
            defaults=dict(deploy_way=self.company_data.deploy_way,
                          validity_days=self.company_data.validity_days,
                          grid=grid,
                          cli_version=self.company_data.cli_version,
                          open_station_time=self.company_data.open_station_time,
                          close_station_time=self.company_data.close_station_time,
                          sales=self.company_data.sales,
                          classify=1,
                          pre_sales=self.company_data.pre_sales,
                          oper_cslt=self.company_data.oper_cslt,
                          impl_cslt=self.company_data.impl_cslt,
                          oper_supt=self.company_data.oper_supt, ),
            company_id=self.company_data.company_id,
        )
        return station_info

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

    def create_open_station(self, company_info, station_info, online_status):
        open_station, _ = OpenStationManage.objects.update_or_create(
            defaults=dict(online_status=online_status,
                          company_info=company_info,
                          station_info=station_info, ),
            station_info__company_id=self.site_id,
        )
        return open_station

    def create_contact_info(self, open_station):
        contact_info = ContactInfo.objects.create(
            station=open_station,
            linkman=self.company_data.link_man,
            link_phone=self.company_data.link_phone,
            link_email=self.company_data.link_email,
            link_qq=self.company_data.link_qq
        )
        return contact_info

    def create_company_url(self, company_info):
        CompanyUrl.objects.filter(company_info__open_station__station_info__company_id=self.site_id).delete()
        if self.company_data.company_url:
            CompanyUrl.objects.create(
                company_url=self.company_data.company_url,
                company_info=company_info
            )

    def create_account_conf(self, open_station):
        AccountConf.objects.filter(station__station_info__company_id=self.site_id).delete()
        AccountConf.objects.create(
            user_name=self.company_data.user_name,
            set_pwd=self.company_data.set_pwd,
            station=open_station,
        )

    def create_func_list(self, open_station: OpenStationManage):
        objs = set()
        for func_code, value in self.func_data.items():
            # 选择
            selection = SingleSelection.objects.filter(function__func_code=func_code, select_value=value).first()
            if func_code not in ('kfsum','contime'):
                value = 0 if value is None else value
                slc = SingleSelection.objects.filter(select_value=value, function__func_code=func_code).first()
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

        except DatabaseError as e:
            logger.error(
                f"error occurred when storing {self.company_data.company_id}\nerror info: {e}\n"
                f"current variables:\n{self.company_data}\n{self.func_data}\n")

    def create_pact_product(self, station_info):
        products = Product.objects.all()
        station_info.pact_products.set(products)


class GridMigrateManager(object):
    def __init__(self, grid_name):
        """初始化，获取本地数据库的节点和其对应的数据库信息"""
        self.grid_name = grid_name
        try:
            self.grid = Grid.objects.get(grid_name=grid_name)

        except Grid.DoesNotExist:
            raise Grid.DoesNotExist(f"该节点未添加，请确认！{grid_name}")
        self.conn = self.get_db_conn('kf')
        #self.oaconn = self.get_db_conn('oa')
        self.aliconn = self.ali_dbcon_kf()
        self.site_ids = self.get_site_ids()

    def get_oa_info(self, siteid):
        """获取企业id在oa库中信息"""
        oa_sql = "select company_prov as oa_prov," \
                 "company_city as oa_city," \
                 "company_address as oa_address," \
                 "company_email as oa_email," \
                 "industry_involved as oa_industry," \
                 "salesman as oa_sales," \
                 "beforesales_personnel as oa_pre_sales," \
                 "aftersales_personnel as oa_oper_cslt," \
                 "integration as oa_impl_cslt," \
                 "training as oa_oper_supt " \
                 "from xn_customer where siteid='%s' limit 1" % (siteid)
        oa_data = self.oaconn.get(oa_sql)
        return oa_data

    def start(self):
        """主流程，构造SQL语句，从远程kf库中的t2d_enterpriseinfo、t2d_enterpriseinfo_extend、t2d_user三个表中取出开站所需的各种
        必要信息，以供后续SiteManager创建本地信息所需
        数据全部取出并解析后，创建一个SiteManager对象并将取到的该site的信息传入，开始下一步，创建本地表信息的"""
        for site_id in self.site_ids:
            enterprise_info_sql = "SELECT siteid, linkman, phone, url, name AS company_name, province," \
                                  " city, addr, email, mode, deadline, classify, online_time_trial" \
                                  " FROM t2d_enterpriseinfo WHERE siteid = '%s'" % site_id
            user_sql = "SELECT name AS username, password FROM t2d_user WHERE siteid = '%s'" \
                       "AND name NOT IN ('ntalker_maliqun', 'ntalker_steven', 'ntalker_lizhipeng', 'ralf') " \
                       "ORDER BY id ASC LIMIT 1" % site_id
            func_sql = "SELECT erpserver, iscommodity, isweixin, autoconnect, iserp, ticket, smarteye, " \
                       "enable_artificialgreeting, changecsr, xiaonengver, watchqueue, autoexpansion, isnoim, " \
                       "transferfiles, close_im_flash, close_tchat_flash, resize_chat, drag_chat, " \
                       "enable_robotgreeting, notrail, captureimage, sessioncarry, viewchatrecord, enable_entrance, " \
                       "androidtransf, othertransf, sessionmode, mode, sessionhelp, wap, waphref, chatingrecord," \
                       "filter, sessiontakeover, isrecep_time, contime, kfsum " \
                       "FROM t2d_enterpriseinfo WHERE siteid = '%s'" % site_id
            extend_func_sql = "SELECT linechannel, is_qq, is_weibo,reversechat,isyqhh,ishhlx " \
                              "FROM t2d_enterpriseinfo_extend WHERE siteid = '%s'" % site_id
            grid_sql = "SELECT t2dmqttserver FROM t_wdk_sit WHERE sitid = '%s'" % site_id
            company_data = self.conn.get(enterprise_info_sql)
            user_data = self.conn.get(user_sql)
            if user_data:
                try:
                    company_data.update(user_data)
                except:
                    continue
            grid_data = self.conn.get(grid_sql)
            if not grid_data:
                logger.error(f"{site_id}在t_wdk_sit中未找到数据")
                continue
            try:
                company_data.update(grid_data)
            except:
                continue
            func_result = ObjDict()
            func_data = self.conn.query(func_sql)
            extend_func_data = self.conn.query(extend_func_sql)
            if func_data:
                func_result.update(func_data[0])
            if extend_func_data:
                func_result.update(extend_func_data[0])
            result = ObjDict(company_data=self.parse_company_data(company_data),
                             func_data=self.parse_func_data(func_result))
            site_manager = SiteManager(result)
            site_manager.start()

    def parse_company_data(self, data):
        """将公司信息、站点信息、管理人员信息解析成为需要的结构"""
        open_station_time = timestamp_to_date(data.online_time_trial * 1000)
        close_station_time = timestamp_to_date(data.deadline * 1000)
        email = data.email if data.email else "0"
        service_area = data.province if data.province else "0"
        industry = data.classify if data.classify else "其他"
        sales = data.oa_sales if data.oa_sales else "0"
        pre_sales = data.oa_pre_sales if data.oa_pre_sales else "0"
        oper_cslt = data.oa_oper_cslt if data.oa_oper_cslt else "0"
        impl_cslt = data.oa_impl_cslt if data.oa_impl_cslt else "0"
        oper_supt = data.oa_oper_supt if data.oa_oper_supt else "0"
        province = data.oa_prov if data.oa_prov else data.province
        city = data.oa_city if data.oa_city else data.city
        address = data.oa_address if data.oa_address else data.addr
        return ObjDict(
            online_status=self.get_online_status(data.mode, close_station_time),
            # company_info
            station_type=self.get_station_type(data.mode),  # 站点类型
            company_name=data.company_name,  # 公司名称
            company_email=email,  # 公司邮箱
            industry=self.get_classify(industry),  # 行业
            GSZZ=0,  # 营业执照
            customer_type=CUSTOM_OLD,  # 客户信息
            service_area=service_area,  # 服务地区

            # station_info
            company_id=data.siteid,  # 站点id
            deploy_way=self.grid.deploy_way,  # 部署信息
            validity_days=(close_station_time - open_station_time).days,  # 有效期
            grid_name=self.grid,  # 节点名称
            cli_version=self.get_cli_version(data.siteid),  # 客户版本 b2b b2c
            # pact_products=Product.objects.all(),  # 绑定产品
            open_station_time=open_station_time,  # 开站时间
            close_station_time=close_station_time,  # 到期时间

            sales=sales,  # 销售人员
            pre_sales=pre_sales,  # 售前人员
            oper_cslt=oper_cslt,  # 运营顾问
            impl_cslt=impl_cslt,  # 实施顾问
            oper_supt=oper_supt,  # 运营支持

            # contact_info
            link_man=data.linkman,
            link_phone=data.phone,
            link_email=data.email,
            link_qq="0",

            # company_address
            province=province,
            city=city,
            address=address,

            # company_url
            company_url=data.url,

            # account_conf
            user_name=data.username,
            set_pwd=data.password,

            real_grid_name=data.t2dmqttserver
        )

    @staticmethod
    def parse_func_data(data):
        """将数据库取出的功能列表信息构造成需要的数据类型"""
        return ObjDict(
            erpserver=data.erpserver,  # erp显示功能开通和关闭 关闭:0,开通:1
            iscommodity=data.iscommodity,  # 商品接口设置功能开通和关闭 关闭:0,开通:1
            isweixin=data.isweixin,  # 微信设置功能开通和关闭 关闭:0,开通:1
            autoconnect=data.autoconnect,  # 连接客服逻辑功能开通和关闭 直接连接:1,输入信息后连接:0
            iserp=data.iserp,  # 开启erp功能开通和关闭 关闭:0,开通:1
            ticket=data.ticket,  # 工单设置功能开通和关闭 关闭:0,开通:1
            smarteye=data.smarteye,  # 帮助中心设置功能开通和关闭 关闭:0,开通:1
            enable_artificialgreeting=data.enable_artificialgreeting,  # 默认欢迎语功能开通和关闭 关闭:0,开通:1
            changecsr=data.changecsr,  # 更换客服功能开通和关闭 关闭:0,开通:1
            xiaonengver=data.xiaonengver,  # 小能版权信息功能开通和关闭 关闭:0,开通:1
            watchqueue=data.watchqueue,  # 客户端查看排队信息功能开通和关闭 关闭:0,开通:1
            autoexpansion=data.autoexpansion,  # 是否展开侧边栏功能开通和关闭 关闭:0,开通:1
            # 更改IM连接级别功能开通和关闭
            # 进入网页就加载im服务,访客关闭聊窗,收到客服发送消息后,弹tip:0,
            # 关闭im服务,访客关闭聊窗,收不到客服发送的消息:1,
            # 打开聊窗后,再加载im服务,访客关闭聊窗,收到客服发送消息后,弹tip:2,
            # 进入网页就加载im服务,访客关闭聊窗,收到客服发送消息后,直接打开聊窗:3
            isnoim=data.isnoim,
            transferfiles=data.transferfiles,  # 访客端是否显示上传文件按钮功能开通和关闭 关闭:0,开通:1
            close_im_flash=data.close_im_flash,  # IM的flash连接功能开通和关闭 关闭:0,开通:1
            close_tchat_flash=data.close_tchat_flash,  # tchat的flash连接功能开通和关闭 关闭:0,开通:1
            resize_chat=data.resize_chat,  # 聊天窗口是否可变换大小功能开通和关闭 关闭:0,开通:1
            drag_chat=data.drag_chat,  # 聊天窗口是否可拖动功能开通和关闭 关闭:0,开通:1
            enable_robotgreeting=data.enable_robotgreeting,  # 是否启用机器人1.0欢迎语开通和关闭 关闭:0,开通:1
            notrail=data.notrail,  # 轨迹调用开通和关闭 进入网页就加载轨迹服务:0,关闭轨迹服务:1,打开聊窗后,再加载轨迹服务:2
            captureimage=data.captureimage,  # 访客端截图插件功能开通和关闭 关闭:0,开通:1
            sessioncarry=data.sessioncarry,  # 会话携带功能开通和关闭 关闭:0,开通:1
            viewchatrecord=data.viewchatrecord,  # 前端查看聊天记录功能开通和关闭 关闭:0,开通:1
            enable_entrance=data.enable_entrance,  # 新版邀请功能开通和关闭 关闭:0,开通:1
            androidtransf=data.androidtransf,  # WAP图片上传功能（安卓）功能开通和关闭 关闭:0,开通:1
            othertransf=data.othertransf,  # WAP图片上传功能（非安卓）功能开通和关闭 关闭:0,开通:1
            sessionmode=data.sessionmode,  # 是否开通公平模式功能开通和关闭 关闭:0,开通:1
            mode=data.mode,  # 小能使用模式 official 正式版 trial 试用版
            sessionhelp=data.sessionhelp,  # ??? 关闭:0，开通:1
            wap=data.wap,  # WAP聊窗功能开关功能开通和关闭 关闭:0,开通:1
            waphref=data.waphref,  # 打开链接方式功能开通和关闭 关闭:0,开通:1
            chatingrecord=data.chatingrecord,  # 聊天记录是否可导出功能开通和关闭 关闭:0,开通:1
            filter=data.filter,  # 敏感词开关功能开通和关闭 关闭:0,开通:1
            sessiontakeover=data.sessiontakeover,  # 会话接管功能开通和关闭 关闭:0,开通:1
            isrecep_time=data.isrecep_time,  # 接待时间功能开通和关闭 关闭:0,开通:1
            contime=data.contime,  # 会话断开时间功能 单位秒
            kfsum=data.kfsum,  # 客服坐席数功能 单位/人
            linechannel=data.linechannel,
            is_qq=data.is_qq,  # qq功能开通和关闭 关闭:0,开通:1
            is_weibo=data.is_weibo,  # 微博功能开通和关闭 关闭:0,开通:1
            reversechat=data.reversechat,  # （教育版）咨询接待-邀请会话功能开通和关闭 关闭:0,开通:1
            isyqhh=data.isyqhh,  # （（教育版）KPI-邀请会话功能开通和关闭 关闭:0,开通:1
            ishhlx=data.ishhlx  # （教育版）数据分析 - 运营报表功能开通和关闭 关闭:0,开通:1
        )

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()

    @staticmethod
    def get_cli_version(site_id: str):
        """判断site_id的版本"""
        start, end = site_id.split("_")
        if start == "kf":
            return CLI_B2C
        elif start != "kf" and end == "1000":
            return CLI_B2B

    @staticmethod
    def get_station_type(mode: str):
        """ 通过mode的值获取站点的类型"""
        mode = mode.lower()
        if mode == "official":
            return STATION_OFFICAL
        elif mode == "trial":
            return STATION_TRIAL
        else:
            return STATION_TRIAL

    @staticmethod
    def get_classify(classify):
        """获取行业信息, 如果源数据不存在则返回其他行业"""
        if not classify:
            return Industry.objects.get(industry="其他")
        industry, _ = Industry.objects.get_or_create(industry=classify)
        return industry

    def get_site_ids(self):
        """获取当前节点下所有的site_id列表，
        只筛选出B2B和B2C的site_id，其他则抛弃"""

        def key(x):
            try:
                start, end = x.split("_")
            except Exception:
                logger.error(f"{x} invalid siteid")
                return False
            if start == "kf":
                return True
            elif start != "kf" and end == "1000":
                return True
            else:
                return False

        # return对应节点下的所有site_id列表
        sql = f'SELECT siteid FROM t2d_route_url where scripturl="http://{self.grid_name}.ntalker.com/js/b2b/" or scripturl="http://{self.grid_name}.ntalker.com/js/xn6/" or scripturl="http://{self.grid_name}-dl.ntalker.com/js/xn6/" or scripturl="http://{self.grid_name}-dl.ntalker.com/js/b2b/"'
        print(sql)
        lines = self.aliconn.query(sql)
        site_ids = [line["siteid"] for line in lines]
        # 只保留b2b b2c
        return list(filter(key, site_ids))

    def get_db_conn(self, dbname):
        """获得kf库的mysql连接对象"""
        db = self.grid.db_info.get(db_name="kf")
        return Connection(
            database=dbname,
            host=db.db_address,
            port=db.db_port,
            user=db.db_username,
            password=decrypt(db.db_pwd),
        )

    def ali_dbcon_kf(self):
        return Connection(
            database='kfrouting',
            host='rdsrypnu7hzxe7f5iwdt7public.mysql.rds.aliyuncs.com',
            port=3306,
            user='ntreaderv',
            password='8qrl177!',
        )

    def get_online_status(self, mode, deadline):
        """如果是正式版，且过期，则状态为关，
        如果是测试版，开
        如果是正式版，且未过期，开"""
        station_type = self.get_station_type(mode)
        if station_type == STATION_OFFICAL and deadline < datetime.date.today():
            return False
        return True


class Command(BaseCommand):
    """可以输入多个节点名称"""

    def add_arguments(self, parser):
        parser.add_argument('grid_name', nargs='+', type=str)

    def handle(self, *args, **options):
        for grid_name in options["grid_name"]:
            manager = GridMigrateManager(grid_name)
            manager.start()
