import time
from urllib import parse
from libs.classic_service.configjs import Configjs
from libs.classic_service.functionset import Functionset
from libs.classic_service.basehelp import *
from libs.basemodel import *
from libs.classic_service.classic_model import *
from ldap_server.configs import VERSION_ID
from libs.classic_service.logic import del_siteid_logic, push_siteid_logic, close_siteid_logic


# 关闭站点
def close_siteid(siteid, oa_dbcon):
    try:
        # oa获取需要开站的企业基本详细信息
        stationinfo_data = BaseModelHelp().get_workorder_info(siteid)
        if stationinfo_data == False:
            return {'status': False, 'error': 'stationinfo is empty'}
        grid_id = stationinfo_data[0]['station_info__grid_id']
        kf_dbcon = BaseModelHelp().get_grid_dbcon(grid_id=grid_id,dbname='kf')
        close_siteid_logic(kf_dbcon, siteid)
        return {'status': True, 'error': 'null'}
    except Exception as e:
        return {'status': False, 'error': 'null'}


# 获取创建站点所需信息
def push_siteid(siteid, oa_dbcon):
    stationinfo_data = BaseModelHelp().get_workorder_info(siteid)
    grid_id = stationinfo_data[0]['station_info__grid_id']
    # 版本id
    version_id = dict(VERSION_ID)[stationinfo_data[0]['station_info__version_id']]
    # kf数据库连接
    kf_dbcon = BaseModelHelp().get_grid_dbcon(grid_id=grid_id, dbname='kf')
    # letao数据库连接
    letao_dbcon = BaseModelHelp().get_grid_dbcon(grid_id=grid_id, dbname='letaotrailcenter')
    # 自定义用户密码
    accountconf_pwd = stationinfo_data[0]['account_conf__set_pwd']
    # 自定义用户账号
    accountconf_username = stationinfo_data[0]['account_conf__user_name']
    # 企业名称
    name = stationinfo_data[0]['company_info__company_name']
    # 创建时间
    createtime = int(time.time())
    timeArray = time.strptime(str(stationinfo_data[0]['station_info__close_station_time']), "%Y-%m-%d")
    # 站点到期时间
    deadline = int(time.mktime(timeArray))
    timeArray = time.strptime(str(stationinfo_data[0]['station_info__open_station_time']), "%Y-%m-%d")
    # 站点开通时间
    online_time_trial = int(time.mktime(timeArray))
    # 默认测试账号密码
    passIndex_ntalker_steven = md5Encode(
        "ntalker_steven" + settings.MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
    # 系统内置ntalker_steven密码
    passIndex_ntalker_steven = passIndex_ntalker_steven[0:8]
    passIndex_ntalker_lizhipeng = md5Encode(
        "ntalker_lizhipeng" + settings.MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
    # 系统内置ntalker_lizhipeng密码
    passIndex_ntalker_lizhipeng = passIndex_ntalker_lizhipeng[0:8]
    passIndex_ralf = md5Encode(
        "ralf" + settings.MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
    # 系统内置ralf密码
    passIndex_ralf = passIndex_ralf[0:8]
    ali_dbcon_kf = MysqldbHelper(CUSTORM_HOST, CUSTORM_USER, CUSTORM_PASSWORD, 'kf', CUSTORM_PORT)
    passIndex_maliqun = KfModel(ali_dbcon_kf).get_t2d_user('ntalker_maliqun')
    # 系统内置maliqun密码
    passIndex_ntalker_maliqun = passIndex_maliqun[0]['password']
    historyurl_address = BaseModelHelp().get_workorder_seraddress(siteid, 'historyurl')
    if historyurl_address[0]['server_grp__ser_address__ser_address']:
        parts = parse.urlparse(historyurl_address[0]['server_grp__ser_address__ser_address'])
        # 路由host
        host = parts.netloc
    else:
        return {'status': False, 'error': 'host is empty'}
    # 根据企业id 功能列表
    func_lists = BaseModelHelp().get_prod_function(siteid)
    # 根据节点找服务组 根据服务组找服务 根据服务找地址t_wdk_sit
    fuwu_data = BaseModelHelp().get_workorder_seraddress(siteid)
    version = checkversion(siteid)
    if version == 'b2b':
        shanghu01_siteid = str(siteid.split('_')[0]) + '_' + str(int(siteid.split('_')[1]) + 1)
        shanghu02_siteid = str(siteid.split('_')[0]) + '_' + str(int(siteid.split('_')[1]) + 2)
        b2b_siteid_lists = [siteid, shanghu01_siteid, shanghu02_siteid]
        data = ''
        for k in b2b_siteid_lists:
            data = push_siteid_logic(kf_dbcon, letao_dbcon, siteid=k, createtime=createtime,
                                     deadline=deadline,
                                     online_time_trial=online_time_trial, name=name, version_id=version_id,
                                     accountconf_username=accountconf_username, accountconf_pwd=accountconf_pwd,
                                     passIndex_ralf=passIndex_ralf,
                                     passIndex_ntalker_lizhipeng=passIndex_ntalker_lizhipeng,
                                     passIndex_ntalker_steven=passIndex_ntalker_steven,
                                     passIndex_ntalker_maliqun=passIndex_ntalker_maliqun, host=host,
                                     func_lists=func_lists,fuwu_lists=fuwu_data)
        return data
    else:
        data = push_siteid_logic(kf_dbcon, letao_dbcon, siteid=siteid, createtime=createtime,
                                 deadline=deadline,
                                 online_time_trial=online_time_trial, name=name, version_id=version_id,
                                 accountconf_username=accountconf_username, accountconf_pwd=accountconf_pwd,
                                 passIndex_ralf=passIndex_ralf, passIndex_ntalker_lizhipeng=passIndex_ntalker_lizhipeng,
                                 passIndex_ntalker_steven=passIndex_ntalker_steven,
                                 passIndex_ntalker_maliqun=passIndex_ntalker_maliqun, host=host, func_lists=func_lists,fuwu_lists=fuwu_data)
        return data


# 删除站点
def del_siteid(siteid, oa_dbcon):
    try:
        # oa获取需要开站的企业基本详细信息
        stationinfo_data = BaseModelHelp().get_workorder_info(siteid)
        if stationinfo_data == False:
            return {'status': False, 'error': 'stationinfo is empty'}
        grid_id = stationinfo_data[0]['station_info__grid_id']
        kf_dbcon = BaseModelHelp().get_grid_dbcon(grid_id=grid_id, dbname='kf')
        del_siteid_logic(kf_dbcon, siteid)
        return {'status': True, 'error': 'null'}
    except Exception as e:
        return {'status': False, 'error': 'null'}
