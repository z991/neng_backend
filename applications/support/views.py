import json

from django.http import JsonResponse
from rest_framework.decorators import api_view, list_route, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from libs.basemodel import BaseModelHelp
from applications.log_manage.models import OperateLog
from libs.classic_service.classic_model import AliModel,KfModel,LetaoModel
from libs.excel_base import Excel_export
from urllib.request import urlopen
from xml.etree.ElementTree import parse
from applications.support.models import ClientDownload
from applications.support.serializers import ClientDownloadSerializers
from applications.setup.permissions import ScriptPermission, OperatingToolsPermission
from libs.celery_task.manage_classic_pwd import classic_pwd
from threading import Thread
from libs.redis import *
from libs.redis import Redis_base
from time import sleep

# 获取grid数据库游标
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def get_grid_dbcon(request):
    grid_id = request.GET['grid_id']
    if grid_id:
        kfcon = BaseModelHelp().get_grid_dbcon(dbname='kf',grid_id=grid_id)
        letaocon = BaseModelHelp().get_grid_dbcon(dbname='letaotrailcenter', grid_id=grid_id)
        if kfcon and letaocon:
            return JsonResponse({"state": True}, safe=False)
        else:
            return JsonResponse({"state": False}, safe=False)
    else:
        return Response({'error': '请先选择grid'}, status=status.HTTP_400_BAD_REQUEST)

# kf操作
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def kf_manage(request):
    grid_id = request.GET.get('grid_id','')
    export = request.GET.get('export','')
    if grid_id:
        kfcon = BaseModelHelp().get_grid_dbcon(dbname='kf', grid_id=grid_id)
        sql = request.GET['sql']
        if "password" in sql:
            return Response({'error': '带有敏感字符'}, status=status.HTTP_400_BAD_REQUEST)
        sql = f"{sql} limit 100"
        data = kfcon.select(sql)
        if data == False:
            return Response({'error': '该节点无数据'}, status=status.HTTP_400_BAD_REQUEST)
        title = []
        for key in list(data):
            title = list(key.keys())
            key['password'] = ''
        if export:
            d = {}
            for key in title:
                d[key] = key
            return Excel_export('weixin-site-list', d, list(data)).export_csv()
        else:
            return JsonResponse(list(data), safe=False)
    else:
        return Response({'error': '请先选择grid'}, status=status.HTTP_400_BAD_REQUEST)

# letao操作
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def letao_manage(request):
    grid_id = request.GET.get('grid_id','')
    export = request.GET.get('export','')
    if grid_id:
        letaocon = BaseModelHelp().get_grid_dbcon(dbname='letaotrailcenter', grid_id=grid_id)
        sql = request.GET['sql']
        if "password" in sql:
            return Response({'error': '带有敏感字符'}, status=status.HTTP_400_BAD_REQUEST)
        sql = f"{sql} limit 100"
        data = letaocon.select(sql)
        if data == False:
            return Response({'error': '该节点无数据'}, status=status.HTTP_400_BAD_REQUEST)
        title = []
        for key in list(data):
            title = list(key.keys())
            key['password'] = ''
        if export:
            d = {}
            for key in title:
                d[key] = key
            return Excel_export('weixin-site-list', d, list(data)).export_csv()
        else:
            return JsonResponse(list(data), safe=False)
    else:
        return Response({'error': '请先选择grid'}, status=status.HTTP_400_BAD_REQUEST)

# grid列表
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def get_grid_list(request):
    data = BaseModelHelp().get_grid_list()
    return JsonResponse(list(data), safe=False)


# 客户查服务器
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def get_siteid_server(request):
    siteid = request.GET['siteid']
    aliobj = AliModel()
    routing = aliobj.get_siteid_routing(siteid)
    gridname = aliobj.get_url_gridname(routing[0]['scripturl'])
    kfcon = BaseModelHelp().get_grid_dbcon(gridname=gridname,dbname='kf')
    sql = f"select a.siteid,a.name,a.url,a.version_id,b.historyurl,b.spamserver,b.fileserver,b.t2dserver,b.tchatserver,b.trailserver,b.crmserver,b.dir,b.t2dmqttserver,b.tchatmqttserver,b.queryurl,b.robotserver from t2d_enterpriseinfo a, t_wdk_sit b where b.sitid='{siteid}' and a.siteid=b.sitid"
    data = kfcon.select(sql)
    if data == False:
        return Response({'error': '该节点无数据'}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(list(data), safe=False)


# 查grid下面的客户
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def get_server_siteid(request):
    grid_id = request.GET.get('grid_id','')
    #export=1为导出，默认等于0
    export = request.GET.get('export','')
    if grid_id:
        data_list = BaseModelHelp().get_grid_siteid(grid_id)
        siteid_str = ''
        for key in list(data_list):
            siteid_str += '"' + key['company_id'] + '",'
        siteid_str = siteid_str[:-1]
        data = AliModel().get_siteid_routing_list(siteid_str)
        if data == False:
            return Response({'error': '该节点无数据'}, status=status.HTTP_400_BAD_REQUEST)
        datas = []
        for key in list(data):
            _datas = {}
            for k in list(data_list):
                if key['siteid'] == k['company_id']:
                    _datas['siteid'] = key['siteid']
                    _datas['name'] = k['open_station__company_info__company_name']
            datas.append(_datas)
        if export:
            title = {"siteid": "企业id", "name": "企业名称"}
            return Excel_export('site-list', title, datas).export_csv()
        else:
            return JsonResponse(datas, safe=False)
    else:
        return Response({'error': '请先选择grid'}, status=status.HTTP_400_BAD_REQUEST)


# 客户查微信
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def get_siteid_weixin(request):
    grid_id = request.GET.get("grid_id", '')
    export = request.GET.get('export','')
    if grid_id:
        try:
            kfcon = BaseModelHelp().get_grid_dbcon(dbname='kf', grid_id=grid_id)
            data = KfModel(kfcon).get_weixin_list()
            if export:
                title = {"openid": "openid", "企业ID": "企业id", "企业名称": "企业名称", '微信公众号': "微信公众号"}
                return  Excel_export('weixin-site-list', title, data).export_csv()
            else:
                return JsonResponse(list(data), safe=False)
        except:
            return Response({'error': '该节点无数据'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': '请先选择grid'}, status=status.HTTP_400_BAD_REQUEST)


# 补订单
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def supply_order(request):
    grid_id = request.GET.get("grid_id", '')
    siteid = request.GET['siteid']
    price = request.GET['price']
    date = request.GET['date']
    clientid = request.GET['clientid']
    userid = request.GET['userid']
    ordernum = request.GET['ordernum']
    try:
        letaocon = BaseModelHelp().get_grid_dbcon(dbname='letaotrailcenter', grid_id=grid_id)
        data = LetaoModel(letaocon).get_region_code(siteid)
        clientid = data[0][clientid]
        LetaoModel(letaocon).modify_keypage_hits(siteid=siteid,date=date,price=price,userid=userid,ordernum=ordernum,clientid=clientid)
        return JsonResponse(True, safe=False)
    except:
        return JsonResponse(False, safe=False)


# 轨迹查询
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def get_user_trail(request):
    try:
        userid = request.GET['userid']
        siteid = userid.split('_')
        siteid = siteid[0] + '_' + siteid[1]
        data = BaseModelHelp().get_workorder_seraddress(siteid,'trailserver')
        trail_url = data[0]['server_grp__ser_address__ser_address'] + f'/uids={userid}&type=3'
        return JsonResponse({'url': trail_url}, safe=False)
    except Exception as e:
        return Response({'error': 'userid输入错误', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 获取机器人
@api_view(['GET'])
@permission_classes([OperatingToolsPermission, ])
def get_robot(request):
    grid_id = request.GET.get("grid_id", '')
    export = request.GET.get('export', '')
    if grid_id:
        kfcon = BaseModelHelp().get_grid_dbcon(dbname='kf', grid_id=grid_id)
        data = KfModel(kfcon).get_robot_list()
        if export:
            title = {"siteid": "siteid", "name": "企业名称", "robotversionid": "机器人类型", 'servergroup': "服务器组"}
            return Excel_export('robot-site-list', title, data).export_csv()
        else:
            return JsonResponse(list(data), safe=False)
    else:
        return Response({'error': '请先选择grid'}, status=status.HTTP_400_BAD_REQUEST)

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper

# 执行自动更换经典版系统账号密码（每天）
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def classic_day_pwd(request):
    #查看redis脚本执行状态 进行中=1，已完成=2，执行失败=3
    req = Redis_base().get("classic_day_pwd")
    if req == 1:
        return JsonResponse({}, safe=False)
    else:
        Redis_base().set("classic_day_pwd", 1)
        classic_day_pwd_async()
        request.body = json.dumps({"data": ""}).encode()
        request.method = "SCRIPT"
        OperateLog.create_log(request)
        return JsonResponse({}, safe=False)
@async
def classic_day_pwd_async():
    try:
        classic_pwd().day_pwd()
        #sleep(20)
        Redis_base().set("classic_day_pwd", 2)
    except:
        Redis_base().set("classic_day_pwd", 3)

# 执行自动更换经典版系统账号密码（每两周）
@api_view(['GET'])
@permission_classes([ScriptPermission, ])
def classic_week_pwd(request):
    #查看redis脚本执行状态 进行中=1，已完成=2，执行失败=3
    req = Redis_base().get("classic_week_pwd")
    if req == 1:
        return JsonResponse({}, safe=False)
    else:
        Redis_base().set("classic_week_pwd", 1)
        classic_week_pwd_async()
        request.body = json.dumps({"data": ""}).encode()
        request.method = "SCRIPT"
        OperateLog.create_log(request)
        return JsonResponse({}, safe=False)
@async
def classic_week_pwd_async():
    try:
        classic_pwd().week_pwd()
        #sleep(20)
        Redis_base().set("classic_week_pwd", 2)
    except:
        Redis_base().set("classic_week_pwd", 3)


class ClientDownSet(viewsets.ModelViewSet):
    """
    客户端下载相关
    """
    queryset = ClientDownload.objects.all().order_by('-id')
    serializer_class = ClientDownloadSerializers
    permission_classes = [OperatingToolsPermission]

    def get_queryset(self):
        queryset = ClientDownload.objects.all().order_by('-id')
        classify = self.request.GET.get('classify', "1").strip()

        if classify:  # 版本分类查询
            queryset = queryset.filter(classify=classify)
        return queryset

    @list_route(['GET'])
    def get_client_url(self, request):
        siteid = self.request.GET.get('siteid', '')
        if siteid:
            url = f'http://update.ntalker.com/update/clientupdate.php?siteid={siteid}'
            # resp = requests.get(url=url, timeout=5)
            u = urlopen(url)
            doc = parse(u)
            root = doc.getroot()
            url = root[1].text.strip()
            exit = ClientDownload.objects.filter(down_address=url).exists()
            if exit == False:
                return JsonResponse({'url': f'表中无{url},请及时添加'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'url': url}, status=status.HTTP_200_OK)
        else:
            return Response({'error': '请输入企业id'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = request.data
        down_a = data.get("down_address")
        exits = ClientDownload.objects.filter(down_address=down_a).exists()
        # 检验新增的下载地址是否已经存在
        if exits == True:
            return Response({"error": f"该下载地址{down_a}已存在"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)








