"""
orm获取项目model
"""
from applications.production_manage.models import Product, FunctionInfo, SingleSelection, DataBaseInfo, Grid
from applications.workorder_manage.models import StationInfo, OpenStationManage
from libs.classic_service.mysqldbhelper import MysqldbHelper
from libs.hash import decrypt
import logging
logger = logging.getLogger('django')


class BaseModelHelp:
    # 获取开站企业所有功能开关
    def get_prod_function(self, siteid):
        queryset = OpenStationManage.objects.filter(station_info__company_id=siteid) \
            .prefetch_related('func_list__select_value', 'func_list__function__func_code') \
            .values('func_list__select_value', 'func_list__function__func_code')
        return list(queryset)

    # 获取开站企业基本信息
    def get_workorder_info(self, siteid):
        queryset = OpenStationManage.objects.filter(station_info__company_id=siteid) \
            .prefetch_related('station_info__grid_id', 'station_info__company_id', 'station_info__version_id',
                              'station_info__company_id',
                              'station_info__open_station_time', 'station_info__open_station_time',
                              'station_info__close_station_time', 'company_info__company_name',
                              'company_info__company_email', 'company_info__service_area', 'account_conf__user_name',
                              'account_conf__set_pwd') \
            .values('station_info__grid_id', 'station_info__company_id', 'station_info__version_id',
                    'station_info__company_id',
                    'station_info__open_station_time', 'station_info__open_station_time',
                    'station_info__close_station_time', 'company_info__company_name', 'company_info__company_email',
                    'company_info__service_area', 'account_conf__user_name', 'account_conf__set_pwd')
        return list(queryset)

    # 根据节点找服务组 根据服务组找服务 根据服务找地址t_wdk_sit
    def get_workorder_seraddress(self, siteid, ser_id=False):
        if ser_id == False:
            queryset = StationInfo.objects.filter(company_id=siteid) \
                .prefetch_related('server_grp__ser_address__ser_address', 'server_grp__ser_address__server__ser_id') \
                .values('server_grp__ser_address__ser_address', 'server_grp__ser_address__server__ser_id')
        else:
            queryset = StationInfo.objects.filter(company_id=siteid).filter(
                server_grp__ser_address__server__ser_id=ser_id) \
                .prefetch_related('server_grp__ser_address__ser_address', 'server_grp__ser_address__server__ser_id') \
                .values('server_grp__ser_address__ser_address', 'server_grp__ser_address__server__ser_id')
        return list(queryset)

    # 根据企业id获取getFlashserver
    def get_grid_getFlashserver(self, siteid):
        queryset = Grid.objects.filter(station_info__company_id=siteid).values('domain_name', 'getFlashserver',
                                                                               'visitors')
        return list(queryset)

    # 根据id获取getFlashserver
    def get_grid_getFlashserver_id(self, grid):
        queryset = Grid.objects.filter(pk=grid).values('domain_name', 'getFlashserver', 'visitors')
        return list(queryset)

    # 根据dbname获取指定数据库列表
    def get_db_list_con(self, dbname):
            queryset = DataBaseInfo.objects.filter(db_name=dbname).values('db_type', 'db_address', 'db_name', 'db_username', 'db_pwd',
                                                               'db_port', 'grid')
            db_list_con = []
            for dbinfo in queryset:
                grid_dbhost = dbinfo['db_address'].strip()
                grid_dbuser = dbinfo['db_username'].strip()
                grid_dbpwd = dbinfo['db_pwd'].strip()
                grid_dbprot = int(dbinfo['db_port'].strip())
                try:
                    grid_dbcon = MysqldbHelper(grid_dbhost, grid_dbuser, decrypt(grid_dbpwd), dbname, grid_dbprot)
                    db_list_con.append(grid_dbcon)
                except:
                    db_list_con.append(grid_dbhost)
                    logging.error('error dbhost:'+grid_dbhost)
                    continue
            return db_list_con

    # 根据节点名称或者节点id获取grid数据库游标
    def get_grid_dbcon(self, **kwargs):
        gridname = kwargs.get('gridname', '')
        grid_id = kwargs.get('grid_id', '')
        dbname = kwargs.get('dbname','')
        if gridname and dbname:
            queryset = DataBaseInfo.objects.filter(db_name=dbname).filter(grid__grid_name=gridname) \
                .values('db_type', 'db_address', 'db_name', 'db_username', 'db_pwd', 'db_port', 'grid')
        elif grid_id and dbname:
            queryset = DataBaseInfo.objects.filter(db_name=dbname).filter(grid__pk=grid_id) \
                .values('db_type', 'db_address', 'db_name', 'db_username', 'db_pwd', 'db_port', 'grid')
        else:
            return False
        grid_dbhost = queryset[0]['db_address'].strip()
        grid_dbuser = queryset[0]['db_username'].strip()
        grid_dbpwd = queryset[0]['db_pwd'].strip()
        grid_dbprot = int(queryset[0]['db_port'].strip())
        grid_dbcon = MysqldbHelper(grid_dbhost, grid_dbuser, decrypt(grid_dbpwd), dbname, grid_dbprot)
        if grid_dbcon == False:
            return False
        return grid_dbcon

    # 根据节点查该节点下正在使用的企业id
    def get_grid_siteid(self, grid):
        queryset = StationInfo.objects.filter(grid__id=grid) \
            .prefetch_related('open_station__company_info__company_name') \
            .values('company_id', 'open_station__company_info__company_name')
        return queryset

    #获取节点列表
    def get_grid_list(self):
        queryset = Grid.objects.all().values('id', 'grid_name')
        return queryset



