import json
import datetime

from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest, DescribeInstanceMonitorDataRequest
from .models import KsyAliCloud

import logging
from celery import shared_task
logger = logging.getLogger(__name__)

today = datetime.date.today()
oneday = datetime.timedelta(days=1)
yesterday = today-oneday


accessKeyId = 'LTAIu83kithYj2r8'
accessSecret = 'iJwFgK0IKlYudDWEz0THb0zdk8lAF0'
UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

region_list = ["cn-beijing", "cn-hangzhou"]


# 发送请求
def get_do_action(request):
    clt = client.AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')
    request.set_accept_format('json')
    response = clt.do_action_with_exception(request)
    response = str(response, encoding="utf-8")
    responses = json.loads(response)
    return responses


# 获取所有实例id和实例name，拼成字典{"instanceid": "instancename"}
def get_id_name():
    id_name_address = {"cn-beijing": [], "cn-hangzhou": []}
    request = DescribeInstancesRequest.DescribeInstancesRequest()
    for region in region_list:
        request.add_query_param('RegionId', region)
        request.add_query_param('PageSize', 50)
        request.add_query_param('PageNumber', 1)
        response_id_name = get_do_action(request)

        #获取实例数据的总个数和总页数
        totalcount = response_id_name["TotalCount"]
        page = response_id_name["PageSize"]
        total = int(totalcount)//int(page)+2

        #获取所有实例的完整信息
        if total > 1:
            for t in range(1, total):
                    request.add_query_param('PageNumber', t)
                    response = get_do_action(request)
                    instance = response["Instances"]["Instance"]
                    for inst in instance:
                        ip_address = inst.get("EipAddress").get("IpAddress")
                        instanceid = inst.get("InstanceId")
                        instancename = inst.get("InstanceName")
                        #如果绑定公网ip
                        if ip_address:
                            id_name_address[region].append({"instancename": instancename,
                                                            "instanceid": instanceid,
                                                            "ipaddress": ip_address})
    return id_name_address


# 获取实例公网发送流量信息
def get_monitor():
    monitor_list = []
    request = DescribeInstanceMonitorDataRequest.DescribeInstanceMonitorDataRequest()
    for region in region_list:
        request.add_query_param('RegionId', region)
        request.add_query_param('StartTime', '%sT01:00:00Z' % yesterday)
        request.add_query_param('EndTime', '%sT00:00:00Z' % today)
        request.add_query_param('Period', 3600)
        id_name = get_id_name()
        for instance in id_name[region]:
            instanceid = instance["instanceid"]
            instancename = instance["instancename"]
            name = instancename.split("-")
            instance_name = name[0]+'-'+name[2]
            request.add_query_param('InstanceId', instanceid)
            # 获取流量信息
            response_monitor = get_do_action(request)
            instance_monitor = response_monitor["MonitorData"]["InstanceMonitorData"]
            for monitor in instance_monitor:
                result = 0
                sum = int(monitor["InternetTX"])
                result += sum
            date = yesterday
            monitor_dict = {"allocation_id": instanceid,
                            "grid_name": instance_name,
                            "date": date,
                            "sum": result/1024,
                            "cloud": 1}

            monitor_list.append(KsyAliCloud(**monitor_dict))
        ret = KsyAliCloud.objects.bulk_create(monitor_list)
    return ret


# 指定日期同步
def assign_date(StartTime, EndTime):
    monitor_list = []
    request = DescribeInstanceMonitorDataRequest.DescribeInstanceMonitorDataRequest()
    for region in region_list:
        request.add_query_param('RegionId', region)
        request.add_query_param('StartTime', '%sT01:00:00Z' % StartTime)
        request.add_query_param('EndTime', '%sT00:00:00Z' % EndTime)
        request.add_query_param('Period', 3600)
        id_name = get_id_name()
        for instance in id_name[region]:
            instanceid = instance["instanceid"]
            instancename = instance["instancename"]
            name = instancename.split("-")
            instance_name = name[0]+'-'+name[2]
            request.add_query_param('InstanceId', instanceid)
            # 获取流量信息
            response_monitor = get_do_action(request)
            instance_monitor = response_monitor["MonitorData"]["InstanceMonitorData"]
            for monitor in instance_monitor:
                result = 0
                sum = int(monitor["InternetTX"])
                time = monitor["TimeStamp"]
                result += sum
                if str(time)[11:13] == "00":
                    time = datetime.datetime.strptime(time, UTC_FORMAT)
                    date = time-oneday
                    monitor_dict = {"allocation_id": instanceid,
                                    "grid_name": instance_name,
                                    "date": date,
                                    "sum": result/1024,
                                    "cloud": 1}
                    exits = KsyAliCloud.objects.filter(date=monitor_dict["date"],
                                                       sum=monitor_dict["sum"],
                                                       allocation_id=monitor_dict["allocation_id"]).exists()

                    # 避免重复记录
                    if exits == False:
                        monitor_list.append(KsyAliCloud(**monitor_dict))

            ret = KsyAliCloud.objects.bulk_create(monitor_list)

    return ret


@shared_task
def sync_aliyun():
    logger.info("start sync aliyun data")
    get_monitor()
    logger.info("sync ldap aliyun complete")