import json

from threading import Thread
from rest_framework import status
from libs.redis import Redis_base
from libs.datetimes import str_to_date
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from ldap_server.configs import SCRIPT_CONFIGURATION
from applications.log_manage.models import OperateLog
from libs.celery_task.inquires_visitor import ReportManager
from applications.data_manage.task import InquiresFetcherManager, UpdateChannelDataHaiEr

from libs.classic_service.synchronous_function import BaseStart, Command, ForAllSynchronous, \
    ForGridSynchronous, ForSiteSynchronous
from applications.setup.permissions import ScriptPermission

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

# 以站点为维度 反向同步站点
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def update_siteid_open_station(request):
    siteid = request.GET.get('siteid', '')
    if not siteid:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '缺少节点参数'})

    if Redis_base().get("siteid_open_station_status") == 1:
        return Response(status=status.HTTP_200_OK)
    else:
        Redis_base().set("siteid_open_station_status", 1)
        handle_siteid_open_station(siteid)
        request.body = json.dumps({"siteid": siteid}).encode()
        request.method = "SCRIPT"
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)


@async
def handle_siteid_open_station(siteid):
    try:
        info = ForSiteSynchronous(siteid)
        base_info = BaseStart(info.grid_name, info.site_ids)
        base_info.start()

        # 脚本执行状态修改为已完成 = 2
        Redis_base().set("siteid_open_station_status", 2)
        return []
    except Exception as e:
        # 脚本执行状态修改为执行失败 = 3
        Redis_base().set("siteid_open_station_status", 3)
        return e.args
# 以节点为维度 反向同步站点
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def update_grid_open_station(request):
    grid = request.GET.get('grid', '')
    if not grid:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '缺少节点参数'})

    if Redis_base().get("grid_open_station_status") == 1:
        return Response(status=status.HTTP_200_OK)

    else:
        Redis_base().set("grid_open_station_status", 1)

        handle_grid_open_station(grid)
        request.body = json.dumps({"grid": grid}).encode()
        request.method = "SCRIPT"
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)


@async
def handle_grid_open_station(grid):
    try:
        info = ForGridSynchronous(grid)
        base_info = BaseStart(info.grid_name, info.site_ids)
        base_info.start()

        # 脚本执行状态修改为已完成 = 2
        Redis_base().set("grid_open_station_status", 2)
        return []
    except Exception as e:
        # 脚本执行状态修改为执行失败 = 3
        Redis_base().set("grid_open_station_status", 3)
        return e.args


# 以全部站点为维度 反向同步站点
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def update_all_open_station(request):
    if Redis_base().get("all_open_station_status") == 1:
        return Response({"status": 1}, status=status.HTTP_200_OK)
    else:
        handle_update_all_open_station()

        request.body = json.dumps({"data": ""}).encode()
        request.method = "SCRIPT"
        OperateLog.create_log(request)

        Redis_base().set("all_open_station_status", 1)

        return Response(status=status.HTTP_200_OK)


@async
def handle_update_all_open_station():
    try:

        for site_id in ForAllSynchronous().get_all_site_id():
            info = ForSiteSynchronous(site_id)
            try:
                base_info = BaseStart(info.grid_name, info.site_ids)
                base_info.start()

            except Exception as e:
                raise e.args

        # 脚本执行状态修改为已完成 = 2
        Redis_base().set("all_open_station_status", 2)
        return []
    except Exception as e:
        # 脚本执行状态修改为执行失败 = 3
        Redis_base().set("all_open_station_status", 3)
        return e.args


# 重构版  咨询访客量脚本  接口化
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def test_history_channel(request):
    str_date_start = request.GET.get('start_date')
    str_date_end = request.GET.get('end_date')
    start_date = str_to_date(str_date_start)
    end_date = str_to_date(str_date_end)

    if Redis_base().get("history_channel_status") == 1:
        return Response({"status": 1}, status=status.HTTP_200_OK)
    else:
        handle_history_channel(start_date, end_date)

        request.body = json.dumps({"start_date": str_date_start, "end_date": str_date_end}).encode()
        request.method = "SCRIPT"
        OperateLog.create_log(request)

        # 脚本执行状态存储到redis 进行中 = 1
        Redis_base().set("history_channel_status", 1)
    return Response({}, status=status.HTTP_200_OK)


@async
def handle_history_channel(start_date, end_date):
    try:
        info = UpdateChannelDataHaiEr()
        data = info.get_history_data(start_date, end_date)
        # 脚本执行状态修改为已完成 = 2
        Redis_base().set("history_channel_status", 2)
        return data
    except Exception as e:
        # 脚本执行状态修改为执行失败 = 3
        Redis_base().set("history_channel_status", 3)
        return e.args


# 经典版  咨询访客量脚本  接口化
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def get_consult(request):
    str_date_start = request.GET.get('start_date')
    str_date_end = request.GET.get('end_date')
    start_date = str_to_date(str_date_start)
    end_date = str_to_date(str_date_end)
    if not (start_date and end_date):
        return Response({'error': '日期上传错误'}, status=status.HTTP_400_BAD_REQUEST)

    if Redis_base().get("consult_status") == 1:
        return Response({"status": 1}, status=status.HTTP_200_OK)
    else:
        # 脚本执行状态修改为已完成 = 1
        Redis_base().set("consult_status", 1)
        handle_consult(start_date, end_date)
        request.body = json.dumps({"start_date": str_date_start, "end_date": str_date_end}).encode()
        request.method = "SCRIPT"
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)


@async
def handle_consult(start_date, end_date):
    try:
        # 咨询量
        consult_manager = InquiresFetcherManager()
        data = consult_manager.fetch_history(start_date, end_date)
        # 脚本执行状态修改为已完成 = 2
        Redis_base().set("consult_status", 2)
        return {"status": 2}
    except Exception as e:
        # 脚本执行状态修改为执行失败 = 3
        Redis_base().set("consult_status", 3)
        return e.args


# 经典版  咨询访客量脚本  接口化
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def get_visitor(request):
    str_date_start = request.GET.get('start_date')
    str_date_end = request.GET.get('end_date')
    start_date = str_to_date(str_date_start)
    end_date = str_to_date(str_date_end)
    if not (start_date and end_date):
        return Response({'error': '日期上传错误'}, status=status.HTTP_400_BAD_REQUEST)

    if Redis_base().get("visitor_status") == 1:
        return Response({"status": 1}, status=status.HTTP_200_OK)

    else:
        # 脚本执行状态修改为已完成 = 1
        Redis_base().set("visitor_status", 1)
        handle_visitor(start_date, end_date)

        request.body = json.dumps({"start_date": str_date_start, "end_date": str_date_end}).encode()
        request.method = "SCRIPT"
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)


@async
def handle_visitor(start_date, end_date):
    try:
        # 访客量
        visitor_manage = ReportManager()
        data = visitor_manage.get_historys(start_date, end_date)
        # 脚本执行状态修改为已完成 = 2
        Redis_base().set("visitor_status", 2)
        return data
    except Exception as e:
        # 脚本执行状态修改为执行失败 = 3
        Redis_base().set("visitor_status", 3)
        return e.args


# 展示脚本名称
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def get_script_name(request):
    serializer = OperateLog.objects.all().filter(action=110).order_by('operationtime')\
        .values('user', 'operationmodule', 'operation', 'operationtime')
    data = []

    for index, name in dict(SCRIPT_CONFIGURATION).items():
        inner_dict = dict()
        inner_dict["script_name"] = name
        inner_dict["type"] = index
        inner_dict["last_execution_time"] = ''
        inner_dict['start_date'] = ''
        inner_dict['end_date'] = ''

        if serializer:
            for item in serializer:
                if inner_dict["script_name"] == item.get('operationmodule'):
                    inner_dict["last_execution_time"] = item.get('operationtime')

                    script_time = item.get('operation')
                    if script_time:
                        inner_dict['start_date'] = eval(script_time).get('request_body').get('start_date')
                        inner_dict['end_date'] = eval(script_time).get('request_body').get('end_date')

        data.append(inner_dict)
    return Response(data=data, status=status.HTTP_200_OK)


# 获取脚本执行记录
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def get_script_record(request):
    index = request.GET.get('index')
    operationmodule = dict(SCRIPT_CONFIGURATION).get(int(index))
    serializer = OperateLog.objects.all().filter(action=110)\
        .filter(operationmodule=operationmodule).order_by('operationtime') \
        .values('user', 'operationmodule', 'operation', 'operationtime')
    data = []

    if serializer:
        serializer = serializer if len(serializer) < 20 else serializer[:20]
        for item in serializer:
            inner_dict = dict()
            inner_dict["script_name"] = item.get('operationmodule')
            inner_dict["last_execution_time"] = item.get('operationtime')

            script_time = item.get('operation')
            if script_time:
                inner_dict['start_date'] = eval(script_time).get('request_body').get('start_date')
                inner_dict['end_date'] = eval(script_time).get('request_body').get('end_date')
            else:
                inner_dict['start_date'] = ''
                inner_dict['end_date'] = ''
            data.append(inner_dict)
    return Response(data=data, status=status.HTTP_200_OK)




