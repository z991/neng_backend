import json
import datetime
import logging
from datetime import date
from multiprocessing import current_process

from celery import shared_task
from django.db import transaction
from django.db.models import Count, QuerySet
from pymysql import MySQLError

from applications.data_manage.models import InquiriesData, OnlineClientData, OnlineProductData, \
    RefactoringConsultingAndVisitors
from libs.mysql_helper import ObjDict
from applications.production_manage.models import DataBaseInfo, Grid
from applications.workorder_manage.models import OpenStationManage, StationInfo
from ldap_server.configs import REFACTORING_CHANNEL_CHOICES, MODULES_MAP, STATION_OFFICAL
from libs.celery_task.classic_data import ClasicData
from libs.celery_task.influx import InfluxDb
from libs.celery_task.inquires_visitor import ReportManager
from libs.celery_task.powerdog import PowerDog
from libs.celery_task.zabbix import grid_monitor
from libs.datetimes import datetime_delta, dates_during, date_to_str, str_to_date
from libs.hash import decrypt
from libs.celery_task.manage_classic_pwd import classic_pwd
from libs.inquires.inquires_db import InquiresFetcher
from libs.inquires.refactor_channel_consulting import ChannelFetcher
from libs.inquires.refactor_channel_haier import ChannelFetcherHaiEr
from applications.log_manage.models import OperateLog

logger = logging.getLogger(__name__)


@shared_task
def fetch_inquires():
    """celery任务：经典版更新咨询量"""
    logger.info("start fetch inquires data")
    manager = InquiresFetcherManager()
    manager.update_inquires()

    today = date_to_str(date.today())
    re_data = {"request_path": "", "request_method": "SCRIPT",
               "request_body": {"start_date": today, "end_date": today}}
    op_log = OperateLog.objects.all().create(
        operationmodule=MODULES_MAP.get("applications.data_manage.views_script.get_consult"),
        action=110,
        operation=re_data
    )
    op_log.save()
    logger.info("fetch inquires data complete")


@shared_task
def fetch_vistors():
    """celery任务：经典版更新访客量"""
    logger.info("start fetch vistors data")
    manager = ReportManager()
    today = date.today()
    # today = str_to_date('2018-08-24')
    manager.create_update(today)

    today = date_to_str(date.today())
    re_data = {"request_path": "", "request_method": "SCRIPT",
               "request_body": {"start_date": today, "end_date": today}}
    op_log = OperateLog.objects.all().create(
        operationmodule=MODULES_MAP.get("applications.data_manage.views_script.get_visitor"),
        action=110,
        operation=re_data
    )
    op_log.save()
    logger.info("fetch vistors data complete")

@shared_task
def fetch_vistors_yesterday():
    """celery任务：经典版更新访客量"""
    logger.info("start fetch vistors_y data")
    manager = ReportManager()
    manager.update_yesterday()

    yes_day = date_to_str(date.today() + datetime.timedelta(days=-1))
    re_data = {"request_path": "", "request_method": "SCRIPT",
               "request_body": {"start_date": yes_day, "end_date": yes_day}}
    op_log = OperateLog.objects.all().create(
        operationmodule=MODULES_MAP.get("applications.data_manage.views_script.get_visitor"),
        action=110,
        operation=re_data
    )
    op_log.save()
    logger.info("fetch vistors_y data complete")


@shared_task
def fetch_channel_haier():
    """celery任务：更新重构站点渠道咨询量访客量--海尔版/重构新版"""
    logger.info("start fetch channel data")
    info = UpdateChannelDataHaiEr()
    info.start()

    today = date_to_str(date.today())
    re_data = {"request_path": "", "request_method": "SCRIPT",
               "request_body": {"start_date": today, "end_date": today}}
    op_log = OperateLog.objects.all().create(
        operationmodule=MODULES_MAP.get("applications.data_manage.views_script.test_history_channel"),
        action=110,
        operation=re_data
    )
    op_log.save()
    logger.info("fetch channel end")


@shared_task
def history_builder():
    """celery任务：生成历史记录"""
    logging.info("online client info build start")
    client_history_builder = OnlineClientFetcher()
    client_history_builder.update_online_client()
    logging.info("online product info build start")
    product_history_builder = OnlineProductFetcher()
    product_history_builder.update_online_product()
    logging.info("all build complete")


@shared_task
def fetch_day_pwd():
    logging.info("111111111111111111111111111111111111111111")
    """celery任务：经典版系统密码每天变更脚本"""
    classic_pwd().day_pwd()
    op_log = OperateLog.objects.all().create(
        operationmodule=MODULES_MAP.get("applications.support.views.classic_day_pwd"),
        action=110
    )
    op_log.save()


@shared_task
def fetch_week_pwd():
    """celery任务：经典版系统密码每两周变更脚本"""
    classic_pwd().week_pwd()
    op_log = OperateLog.objects.all().create(
        operationmodule=MODULES_MAP.get("applications.support.views.classic_week_pwd"),
        action=110
    )
    op_log.save()


class InquiresFetcherManager(object):
    """该类不负责咨询量查询的过程，只负责总体的调度。执行咨询量查询的某些具体任务时，应尽量在此类中实现"""
    def __init__(self):
        db_info = DataBaseInfo.objects.filter(db_name="kf")
        self.db_list = db_info.values_list("db_address", "db_port", "db_username", "db_pwd").distinct()
        self.today = date.today()
        self.yesterday = datetime_delta(self.today, days=-1)

    def _fetch_data(self, which):
        """获取数据，传入today或者yesterday"""
        result = {}
        for host, port, user, password in self.db_list:
            try:
                fetcher = InquiresFetcher(host=host, port=int(port), user=user, password=decrypt(password))
            except MySQLError as err:
                logger.warning(err)
                continue
            data = getattr(fetcher, "fetch_" + which)()
            for site_id, channel, num in data:
                result.setdefault(site_id, {})
                result[site_id].setdefault(channel, 0)
                result[site_id][channel] += num
            del fetcher
        return result

    def fetch_history(self, from_date, to_date):
        """获取指定时间段内的咨询量
        TODO：单独封装成一个自定义命令，类似 python manage.py fetch_inquires ### ###
        """
        for host, port, user, password in self.db_list:
            try:
                fetcher = InquiresFetcher(host=host, port=int(port), user=user, password=decrypt(password))
            except MySQLError as err:
                logger.warning(err)
                continue
            dates = dates_during(from_date=from_date, to_date=to_date)
            for each in dates:
                logger.info(f"正在获取数据库：{host}， 日期：{each}")
                result = {}
                data = fetcher.fetch_date(each)
                for site_id, channel, num in data:
                    result.setdefault(site_id, {})
                    result[site_id].setdefault(channel, 0)
                    result[site_id][channel] += num
                for site_id, values in result.items():
                    try:
                        station = OpenStationManage.objects.all().get(station_info__company_id=site_id)
                        server_grp = station.station_info.server_grp.group_name if station.station_info.server_grp else 0
                        grid = Grid.objects.get(group__group_name=server_grp).grid_name
                    except:
                        continue
                    n=0
                    for channel, num in values.items():
                        n = n + 1
                        InquiriesData.objects.create(
                            inquires_num=num,
                            date=each,
                            channel=channel,
                            company_id=site_id,
                            industry=station.company_info.industry.industry,
                            deploy_way=station.station_info.deploy_way,
                            cli_version=station.station_info.cli_version,
                            server_grp=server_grp,
                            open_id=station.id,
                            grid=grid,
                        )

    def _to_local_today(self):
        # 1.新增今天的数据
        for site_id, values in self._fetch_data("today").items():
            try:
                station = OpenStationManage.objects.all().get(station_info__company_id=site_id)
                server_grp = station.station_info.server_grp.group_name if station.station_info.server_grp else 0
                grid = Grid.objects.get(group__group_name=server_grp).grid_name
            except:
                continue
            for channel, num in values.items():
                InquiriesData.objects.create(
                    company_id=site_id,
                    industry=station.company_info.industry.industry if station.company_info.industry.industry else 0,
                    server_grp=server_grp,
                    deploy_way=station.station_info.deploy_way if station.station_info.deploy_way else 0,
                    cli_version=station.station_info.cli_version if station.station_info.cli_version else 0,
                    date=self.today,
                    channel=channel,
                    inquires_num=num,
                    open_id=station.id,
                    grid=grid

                )
        # 2.更新昨天的数据
        for site_id, values in self._fetch_data("yesterday").items():
            try:
                station = OpenStationManage.objects.all().get(station_info__company_id=site_id)
                server_grp = station.station_info.server_grp.group_name if station.station_info.server_grp else 0
                grid = Grid.objects.get(group__group_name=server_grp).grid_name
            except:
                continue
            for channel, num in values.items():
                InquiriesData.objects.update_or_create(
                    defaults={"inquires_num": num},
                    date=self.yesterday,
                    channel=channel,
                    company_id=site_id,
                    industry=station.company_info.industry.industry if station.company_info.industry.industry else 0,
                    server_grp=server_grp,
                    deploy_way=station.station_info.deploy_way if station.station_info.deploy_way else 0,
                    cli_version=station.station_info.cli_version if station.station_info.cli_version else 0,
                    open_id=station.id,
                    grid=grid
                )

    def _to_local_yesterday(self):
        # 1.更新今天的数据
        for site_id, values in self._fetch_data("today").items():
            try:
                station = OpenStationManage.objects.all().filter(station_info__company_id=site_id).first()
                server_grp = station.station_info.server_grp.group_name if station.station_info.server_grp else 0
                grid = Grid.objects.get(group__group_name=server_grp).grid_name
            except:
                continue
            for channel, num in values.items():
                try:
                    InquiriesData.objects.update_or_create(
                        defaults={"inquires_num": num},
                        date=self.today,
                        channel=channel,
                        company_id=site_id,
                        industry=station.company_info.industry.industry if station.company_info.industry.industry else 0,
                        server_grp=server_grp,
                        deploy_way=station.station_info.deploy_way if station.station_info.deploy_way else 0,
                        cli_version=station.station_info.cli_version if station.station_info.cli_version else 0,
                        open_id=station.id,
                        grid=grid
                    )
                except:
                    pass

    def update_inquires(self):
        """如果当天的咨询量已存在，则只更新当天的咨询量
        如果当天的咨询量不存在，则说明是当天第一次获取咨询量，第一步更新昨天的咨询量数据，第二步获取今天的咨询量数据
        """
        today_inquires = InquiriesData.objects.all().filter(date=self.today)
        if not today_inquires.exists():
            return self._to_local_today()
        return self._to_local_yesterday()


class OnlineClientFetcher(object):
    def __init__(self):
        self.today = date.today()
        self.values = self._fetch()

    def _fetch(self) -> QuerySet:
        """
        统计条件：
        1. 状态为开
        2. 正式站点
        3. 在有效期内
        """
        return OpenStationManage.objects.all() \
            .filter(online_status=OpenStationManage.STATUS_ONLINE,
                    company_info__station_type=STATION_OFFICAL,
                    station_info__open_station_time__lte=self.today,
                    station_info__close_station_time__gte=self.today) \
            .values_list("company_info__industry__industry",
                         "station_info__deploy_way",
                         "station_info__cli_version") \
            .annotate(count=Count("*"))

    def update_online_client(self) -> None:
        if OnlineClientData.objects.filter(date=self.today).exists():  # 保证每天只会运行一次
            return
        for industry, deploy_way, cli_version, count in self.values:
            OnlineClientData.objects.create(
                date=self.today,
                industry=industry,
                deploy_way=deploy_way,
                cli_version=cli_version,
                online_num=count
            )


class OnlineProductFetcher(object):
    def __init__(self):
        self.today = date.today()
        self.values = self._fetch()

    def _fetch(self) -> QuerySet:
        model = StationInfo.pact_products.through
        return model.objects.all() \
            .filter(stationinfo__open_station__company_info__station_type=STATION_OFFICAL,
                    stationinfo__open_station__online_status=OpenStationManage.STATUS_ONLINE,
                    stationinfo__open_station_time__lte=self.today,
                    stationinfo__close_station_time__gte=self.today) \
            .values_list("product_id",
                         "stationinfo__open_station__company_info__industry__industry",
                         "stationinfo__deploy_way",
                         "stationinfo__cli_version") \
            .annotate(count=Count("*"))

    def update_online_product(self) -> None:
        if OnlineProductData.objects.filter(date=self.today).exists():  # 保证每天只会运行一次
            return
        for product_id, industry, deploy_way, cli_version, count in self.values:
            OnlineProductData.objects.create(
                date=self.today,
                industry=industry,
                deploy_way=deploy_way,
                cli_version=cli_version,
                product_id=product_id,
                online_num=count
            )


class UpdateChannelDataHaiEr:
    """
    如果当天的咨询量已存在，则只更新当天的咨询量
    如果当天的咨询量不存在，则说明是当天第一次获取咨询量，第一步更新昨天的咨询量数据，第二步获取今天的咨询量数据
    """
    def __init__(self):
        self.today = date_to_str(date.today())
        self.yesterday = date_to_str(datetime_delta(date.today(), days=-1))

    # 解析数据
    def parse_data(self, data_list):
        """
        [
            {'siteid': 'kf_100000', 'channel': -1, 'valid_consulting': 23, 'invalid_consulting': 25,
             'uv': 232, 'deploy': 5, 'grid': 'cg-bj', 'industry': '0'},
            {'siteid': 'kf_100000', 'channel': 2, 'valid_consulting': 23, 'invalid_consulting': 25,
             'uv': 232, 'deploy': 5, 'grid': 'cg-bj', 'industry': '0'},
            {.......},......
        ]
        """
        # data_list<<<===>>>{'siteid': site_list, 'vis': vis_dict, 'con': con_dict}

        site_list = data_list['siteid']
        vis_dict = data_list['vis']
        con_dict = data_list['con']
        configs_info = dict(zip(dict(REFACTORING_CHANNEL_CHOICES).values(), dict(REFACTORING_CHANNEL_CHOICES).keys()))

        total_list = []
        for each in site_list:
            value_list = OpenStationManage.objects.all().filter(station_info__classify=2) \
                .filter(station_info__company_id=each) \
                .select_related('company_info__industry__industry', 'station_info__deploy_way',
                                'station_info__grid__grid_name') \
                .values_list('company_info__industry__industry', 'station_info__deploy_way',
                             'station_info__grid__grid_name')
            if not value_list:
                value_list = [('0', 5, 'cg-bj')]
            industry, deploy, grid = value_list[0]
            for channel, v_value, siteid in vis_dict:
                if each == siteid:
                    for con_channel, value, in_value, siteid in con_dict:
                        if each == siteid and channel == con_channel:
                            inner_dict = {'siteid': each, 'channel': configs_info.get(channel), 'uv': v_value,
                                          'deploy': deploy, 'industry': industry, 'grid': grid}
                            total_list.append(inner_dict)
                            inner_dict['valid_consulting'] = value
                            inner_dict['invalid_consulting'] = in_value

        return total_list

    # 更新今天数据
    def get_today_data(self):
        """
        每一天 每个站点至少一条数据 如果这条数据是补录的默认数据，则渠道为未知(-1)咨询访客全为0
        """
        fetcher = ChannelFetcherHaiEr(self.today)
        # 获取今天源数据
        try:
            today_data = fetcher.get_data()

            result = self.parse_data(today_data)

            with transaction.atomic():
                for each in result:
                    s = RefactoringConsultingAndVisitors.objects.update_or_create(
                            date=self.today,
                            company_id=each['siteid'],
                            valid_consulting=each.get('valid_consulting', 0),
                            invalid_consulting=each.get('invalid_consulting', 0),
                            valid_visitors=0,
                            invalid_visitors=0,
                            channel=each['channel'],
                            grid=each['grid'],
                            industry=each['industry'],
                            deploy=each['deploy'],
                            unique_vistor=each.get('uv', 0)
                        )
        except Exception as e:
            logging.info('数据回滚了:' + str(e))
            return '数据回滚了:' + str(e)

    def get_yesterday_data(self):
        """
        获取今天数据 并且更新昨天数据
        """
        # 1.新增今天的数据
        fetcher = ChannelFetcherHaiEr(self.today)
        # 获取今天源数据
        try:
            today_result = fetcher.get_data()
            result = self.parse_data(today_result)
            with transaction.atomic():
                for each in result:
                    RefactoringConsultingAndVisitors.objects.update_or_create(
                        date=self.today,
                        company_id=each['siteid'],
                        valid_consulting=each.get('valid_consulting', 0),
                        invalid_consulting=each.get('invalid_consulting', 0),
                        valid_visitors=0,
                        invalid_visitors=0,
                        channel=each['channel'],
                        grid=each['grid'],
                        industry=each['industry'],
                        deploy=each['deploy'],
                        unique_vistor=each.get('uv', 0)
                    )

        except Exception as e:
            logging.info('数据回滚了:' + str(e))
            return '数据回滚了:' + str(e)

        # 2.更新昨天的数据
        yes_fetcher = ChannelFetcherHaiEr(self.yesterday)
        # 获取昨天源数据
        yes_result = yes_fetcher.get_data()

        result = self.parse_data(yes_result)
        try:
            with transaction.atomic():
                for each in result:
                    s = RefactoringConsultingAndVisitors.objects.update_or_create(
                        date=self.yesterday,
                        company_id=each['siteid'],
                        valid_consulting=each.get('valid_consulting', 0),
                        invalid_consulting=each.get('invalid_consulting', 0),
                        valid_visitors=0,
                        invalid_visitors=0,
                        channel=each['channel'],
                        grid=each['grid'],
                        industry=each['industry'],
                        deploy=each['deploy'],
                        unique_vistor=each.get('uv', 0)
                    )
        except Exception as e:
            logging.info('数据回滚了:' + str(e))
            return '数据回滚了:' + str(e)
        return 'end'

    # 获取历史数据(一段指定时间)
    def get_history_data(self, start_date, end_date):
        for d in dates_during(start_date, end_date):
            dates = date_to_str(d)
            fetcher = ChannelFetcherHaiEr(dates)
            # 获取今天源数据
            history_data = fetcher.get_data()
            # 解析数据
            result = self.parse_data(history_data)
            # 插入数据
            try:
                with transaction.atomic():
                    for each in result:
                        s = RefactoringConsultingAndVisitors.objects.update_or_create(
                            date=dates,
                            company_id=each['siteid'],
                            valid_consulting=each.get('valid_consulting', 0),
                            invalid_consulting=each.get('invalid_consulting', 0),
                            valid_visitors=0,
                            invalid_visitors=0,
                            channel=each['channel'],
                            grid=each['grid'],
                            industry=each['industry'],
                            deploy=each['deploy'],
                            unique_vistor=each.get('uv', 0)
                        )
            except Exception as e:
                logging.info('数据回滚了:' + str(e))
                return '数据回滚了:' + str(e)

    # 执行变更(启动入口)
    def start(self):
        """
        如果当天的咨询量已存在，则只更新当天的咨询量
        如果当天的咨询量不存在，则第一步更新昨天的咨询量数据，第二步获取今天的咨询量数据
        """
        today_inquires = RefactoringConsultingAndVisitors.objects.all().filter(date=self.today)
        if not today_inquires.exists():
            return self.get_yesterday_data()
        return self.get_today_data()


# 抓取ZABBIX数据
@shared_task
def sync_zabbix():
    # 解决'Worker' object has no attribute '_config'报错
    # 参考http://blog.51cto.com/zhenfen/2105628
    current_process()._config = {'semprefix': '/mp'}

    logger.info("start sync zabbix data")
    grid_monitor()
    logger.info("sync zabbix complete")


# 抓取influx数据
@shared_task
def sync_influx():
    logger.info("start sync influx data")
    influx = InfluxDb()
    influx.parse_ms_loss()
    logger.info("sync influx complete")


# 抓取powerdog数据
@shared_task
def sync_powerdog():
    logger.info("start sync powerdog data")
    power_dog = PowerDog()
    power_dog.logic()
    logger.info("sync powerdog complete")


#抓取clssica数据
@shared_task
def sync_classicdata():
    logger.info("start sync classicdata")
    clasic_data = ClasicData()
    clasic_data.logic()
    logger.info("sync classicdata complete")
