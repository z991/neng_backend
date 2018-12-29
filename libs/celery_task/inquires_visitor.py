import logging
from datetime import date

from celery import shared_task
from django.db.models import Count, QuerySet
from pymysql import MySQLError
import time
from applications.data_manage.models import VistorData
from applications.production_manage.models import DataBaseInfo
from applications.workorder_manage.models import OpenStationManage, StationInfo
from applications.production_manage.models import Grid
from ldap_server.configs import STATION_OFFICAL
from libs.datetimes import datetime_delta, dates_during, str_to_date
from libs.hash import decrypt
import datetime
from libs.classic_service.mysqldbhelper import *
import pymysql
from libs.datetimes import str_to_date

from libs.datetimes import datetime_delta, date_to_timestamp, datetime_to_timestamp


class ReportManager:
    def __init__(self):
        db_info = DataBaseInfo.objects.filter(db_name="kf")
        self.db_list = db_info.values_list("db_address", "db_port", "db_username", "db_pwd","grid_id").distinct()

    def fetch_data(self, from_date):
        """
        抓取指定日期的数据
        :param from_date:
        :return:
        """
        cv_dict = {}
        for host, port, user, password, grid_id in self.db_list:
            try:
                self.grid_id = grid_id
                fetcher = GetDataManager(host=host, port=int(port), user=user, password=decrypt(password))
            except MySQLError as err:
                continue
            siteid_arr = StationInfo.objects.filter(grid=grid_id).values_list("company_id")
            db_info = DataBaseInfo.objects.filter(db_name="letaotrailcenter").filter(grid_id=grid_id)

            db_qc = db_info.values_list("db_address", "db_port", "db_username", "db_pwd").distinct()
            if len(db_qc) > 0:
                try:
                    self.db_letao = pymysql.connect(host=db_qc[0][0], user=db_qc[0][2],
                                                    password=decrypt(db_qc[0][3]), database='letaotrailcenter',
                                                    port=int(db_qc[0][1]), charset="utf8", connect_timeout=5)
                    self.cursor_letao = self.db_letao.cursor()
                except:
                    continue
                pv_data = fetcher.get_pv_num(each=from_date,grid_id=self.grid_id,siteid_arr=siteid_arr,cursor_letao=self.cursor_letao)

                result = {}
                for pp4 in pv_data:
                    pk4 = pp4[0]
                    pv4 = pp4[1]
                    if pk4 in result:
                        result[pk4]["pv"]=pv4
                    else:
                        result[pk4]={"pv":pv4}
                for key, values in result.items():
                    company_id = key
                    visitor_num =values.get('pv', 0)
                    cv_dict.update({company_id: visitor_num})
        return cv_dict

    def create_update(self, date):
        """
        新增和更新今天的访客量数据
        :param date:
        :return:
        """
        today = date
        for company_id, visitor_num in self.fetch_data(today).items():
            try:
                stations = OpenStationManage.objects.all().filter(station_info__company_id=company_id)
            except OpenStationManage.DoesNotExist:
                continue
            if stations:
                for station in stations:
                    industry = station.company_info.industry.industry
                    deploy_way = station.station_info.deploy_way
                    grid = Grid.objects.get(station_info__company_id=company_id).grid_name
            else:
                industry = 0
                deploy_way = 0
                grid = 0
            try:
                ret = VistorData.objects.update_or_create(defaults={"visitor_num": visitor_num},
                                                date=today,
                                                company_id=company_id,
                                                industry=industry,
                                                grid=grid,
                                                deploy_way=deploy_way
                                                )
            except:
                pass
        return 'ok'

    def update_yesterday(self):
        """
        更新昨天的数据
        :return:
        """
        today = datetime.date.today()
        yesterday = today + datetime.timedelta(days=-1)

        for company_id, visitor_num in self.fetch_data(yesterday).items():
            try:
                stations = OpenStationManage.objects.all().filter(station_info__company_id=company_id)
            except OpenStationManage.DoesNotExist:
                continue
            if stations:
                for station in stations:
                    industry = station.company_info.industry.industry
                    deploy_way = station.station_info.deploy_way
                    grid = Grid.objects.get(station_info__company_id=company_id).grid_name
            else:
                industry = '其他'
                deploy_way = 0
                grid = "无"
            VistorData.objects.update_or_create(defaults={"visitor_num": visitor_num},
                                                date=yesterday,
                                                company_id=company_id,
                                                industry=industry,
                                                grid=grid,
                                                deploy_way=deploy_way
                                                )
        return 'ok'

    def get_historys(self, from_date, to_date):
        """
        获取指定日期的访客量数据
        :param from_date:
        :param to_date:
        :return:
        """
        for host, port, user, password, grid_id in self.db_list:
            try:
                self.grid_id = grid_id
                fetcher = GetDataManager(host=host, port=int(port), user=user, password=decrypt(password))
            except MySQLError as err:
                continue
            dates = dates_during(from_date=from_date, to_date=to_date)
            for each in dates:
                siteid_arr = StationInfo.objects.filter(grid=grid_id).values_list("company_id")
                db_info = DataBaseInfo.objects.filter(db_name="letaotrailcenter").filter(grid_id=grid_id)

                db_qc = db_info.values_list("db_address", "db_port", "db_username", "db_pwd").distinct()
                data_create_list = []
                if len(db_qc) > 0:
                    try:
                        self.db_letao = pymysql.connect(host=db_qc[0][0], user=db_qc[0][2],
                                                        password=decrypt(db_qc[0][3]),
                                                        database='letaotrailcenter',
                                                        port=int(db_qc[0][1]), charset="utf8", connect_timeout=5)
                        self.cursor_letao = self.db_letao.cursor()
                    except:
                        continue
                    pv_data = fetcher.get_pv_num(each=each, grid_id=self.grid_id, siteid_arr=siteid_arr,
                                                 cursor_letao=self.cursor_letao)
                    result = {}
                    for pp4 in pv_data:
                        pk4 = pp4[0]
                        pv4 = pp4[1]
                        if pk4 in result:
                            result[pk4]["pv"] = pv4
                        else:
                            result[pk4] = {"pv": pv4}

                    for key, values in result.items():
                        stations = OpenStationManage.objects.all().filter(station_info__company_id=key)

                        company_id = key
                        visitor_num = values.get('pv', 0)

                        if stations:
                            for station in stations:
                                industry = station.company_info.industry.industry
                                deploy_way = station.station_info.deploy_way
                                grid = Grid.objects.get(station_info__company_id=key).grid_name
                        else:
                            industry = 0
                            deploy_way = 0
                            grid = 0
                        date_dict = {
                            "company_id": company_id,
                            "industry": industry,
                            "deploy_way": deploy_way,
                            "date": each,
                            "visitor_num": visitor_num,
                            "grid": grid

                        }
                        data_create_list.append(VistorData(**date_dict))
                else:
                    continue
                ret = VistorData.objects.bulk_create(data_create_list)
        return f'{from_date}至{to_date}历史数据同步成功'


class GetDataManager(object):
    def __init__(self, host="", user="", password="", database="kf", port=3306, charset="utf8"):
        try:
            self.db = pymysql.connect(host=host, user=user, password=password, database=database, port=port,
                                      charset=charset, connect_timeout=5)
            self.cursor = self.db.cursor()
        except Exception as e:
            err = f'Cannot connect to MySQL on {host}'

    def get_pv_num(self,each,grid_id,siteid_arr,cursor_letao):
        _datas = []
        for siteid in list(siteid_arr):
            small_datas = []
            sql = f"SELECT region_code FROM t2d_site where website='{siteid[0]}' limit 1"
            cursor_letao.execute(sql)
            _data = cursor_letao.fetchall()
            date_each = ''.join(str(each).split('-'))
            if not _data:
                continue
            tablename = f"t2d_{_data[0][0]}_ip_hits_{date_each}"
            sql = f"select website,count(*) from {tablename} where website='{siteid[0]}' group by website"
            try:
                cursor_letao.execute(sql)
            except:
                continue
            _data = cursor_letao.fetchall()
            small_datas = small_datas + list(_data)
            _datas = _datas + small_datas
        return _datas