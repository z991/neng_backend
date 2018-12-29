"""
function：site_push 推送
describe：开站推送主逻辑文件和两个辅助验证方法
date：20171127
author：gjf
version:1.09
"""
import time
from django.http import JsonResponse
from libs.classic_service.manage_siteid import *
"""
function:infopush
describe:开站推送主逻辑文件和两个辅助验证方法
param: string @siteid
return: json
"""

"""
function:node_msg_notice
describe:根据节点id找对应咨询库；查询节点咨询数量大于2w则不显示该节点
param: int @grid_id 节点id
return: bool
"""
def node_msg_notice(grid_id):
    # oa数据库信息
    try:
        kf_dbcon = BaseModelHelp().get_grid_dbcon(grid_id=grid_id,dbname='kf')
        if kf_dbcon == False:
            return True
        endtime = int(time.time())
        starttime = endtime - 86400
        sql = 'select count(*) from t2d_chatscene where starttime>=%d and starttime<=%d' % (starttime, endtime)
        chatscene_num = kf_dbcon.select(sql)
        if chatscene_num >= 20000:
            return False
        else:
            return True
    except Exception as e:
        return True

#检查企业id是否重复----经典版
def check_siteid_old(siteid):
    # oa数据库信息
    try:
        route_url = AliModel().get_siteid_routing(siteid)
        if route_url==False:
            return True
        else:
            return False
    except Exception as e:
        return False

#检查企业id是否重复----重构版
def check_siteid_new(siteid):
        return True

"""
function:delsiteid
describe:根据节点id找对应咨询库；删除企业id所在的kf库内信息
param: int @grid_id 节点id
param: string @siteid 企业id
return: bool
"""
def delsiteid(siteid):
    try:
        oa_dbcon = dbcon_oa()
        del_siteid(siteid,oa_dbcon)
        return True
    except Exception as e:
        return False

"""
function：site_push 推送
describe：开站推送主逻辑文件和两个辅助验证方法
date：20171127
author：gjf
version:1.09
"""
import time
from django.http import JsonResponse
from libs.classic_service.manage_siteid import *
"""
function:infopush
describe:开站推送主逻辑文件和两个辅助验证方法
param: string @siteid
return: json
"""


def infopush(siteid,online_status):
    # oa数据库信息
    oa_dbcon = dbcon_oa()
    # 根据企业id查询绑定的哪个节点
    if oa_dbcon == False:
        data = {'status': False, 'error': 'oa库连接失败'}
        return JsonResponse(data, safe=False)
    if online_status:
        data = push_siteid(siteid, oa_dbcon)
    else:
        data = close_siteid(siteid, oa_dbcon)
    return JsonResponse(data, safe=False)
