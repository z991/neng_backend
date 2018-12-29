from libs.classic_service.site_push import infopush,delsiteid
from applications.backend import tasks
from libs.classic_service.classic_model import *
from libs.basemodel import BaseModelHelp
from libs.functionset import New_ticket
from django.http import JsonResponse,HttpResponse
from libs.hash import decrypt
from libs.push_service_cg.push_service import Push_manage
from libs.email_ali import Email_base
from threading import Thread
from time import sleep
import xlrd

from datetime import datetime
from xlrd import xldate_as_tuple
from django.http import HttpResponse,JsonResponse
import csv
import codecs
import socket
#测试
def apitest(request):
    siteid = request.GET['siteid']
    data = BaseModelHelp().get_grid_getFlashserver(siteid)
    #return HttpResponse(data)
    return JsonResponse(data,safe=False)

#工单
def new_gongdan(request):
    siteid = request.GET['siteid']
    data = New_ticket.push_ticket(siteid,1)
    return JsonResponse(data,safe=False)
#经典版推送
def push_service_infopush(request):
    siteid = request.GET['siteid']
    data = infopush(siteid,True)
    #data = delsiteid(siteid)
    return data

def checkpwd(request):
    pwd = request.GET['pwd']
    possword = decrypt(pwd)
    return HttpResponse(possword)

def celery_push(request):
    siteid = request.GET['siteid']
    res = tasks.add_task.delay(siteid, 'cg')
    return res

def email(request):
    a = Email_base().email(['guojifa@xiaoneng.cn', 'liuqian@xiaoneng.cn'],
                           '哈喽你好', '', '<b>邮件内容</b><h5>少时诵诗书</h5>223的')
    return HttpResponse(a)
def test(request):

    siteid = request.GET['siteid']
    stationinfo_data = BaseModelHelp().get_workorder_info(siteid)
    grid_id = stationinfo_data[0]['station_info__grid_id']
    # 根据节点获取kf库配置
    kf_dbcon = BaseModelHelp().get_grid_dbcon(grid_id=grid_id,dbname='kf')
    KfModel(kf_dbcon).modify_t2d_site_classify(siteid)
    data = KfModel(kf_dbcon).get_t2d_site_classify(siteid)[0]['id']
    return HttpResponse(data)

def push_cg(request):
    siteid = request.GET['siteid']
    data = Push_manage(siteid,'123test',True).push_data()
    return HttpResponse(data)




