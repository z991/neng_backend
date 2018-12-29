import requests
from requests_aws4auth import AWS4Auth
import json
import datetime

import logging
from celery import shared_task
from .models import KsyAliCloud

logger = logging.getLogger(__name__)

ak = "AKLTckSxExkJTtO00tv5wJKC2Q"
sk = "OOSPNMJATdDBFdeCV9S5GFORetfLhUvCWk/SjwhMmbtGtdJNGbvnChFDaMF6QMVHAw=="
headers = {
    'Accept': 'Application/json'
}
credentials = {
    'ak': ak,
    'sk': sk
}

#region列表
region_list = ['cn-beijing-6', 'cn-shanghai-2']


# 生成实例id和实例名称的字典
def instance_id_name(service, region, **kwargs):
    auth = AWS4Auth(credentials['ak'], credentials['sk'], region, service)
    # 获取host
    host = 'http://%s.%s.api.ksyun.com' % (service, region)
    query = kwargs
    response = requests.get(host, params=query, headers=headers, auth=auth).text
    response = json.loads(response)
    return response


# 实例id用
query_instance = {
        'Action': 'DescribeInstances',
        'Version': '2016-03-04',
        'MaxResults': 1000,
        }
# eip用
query_address = {
        'Action': 'DescribeAddresses',
        'Version': '2016-03-04',
        'MaxResults': 1000,
}


# 生成{instanceid:instancename}字典
def dict_instance():
    instance_dict = {}
    for region in region_list:
        instance = instance_id_name('kec', region, **query_instance)
        instancesset = instance["InstancesSet"]

        for iterm in instancesset:
            instance_idb = iterm.get("InstanceId", "无")
            instance_nameb = iterm.get("InstanceName", "无")
            instance_dict.update({instance_idb: instance_nameb})
    return instance_dict


# 获取绑定资源的eip字典{allocationid:instanceid}
def dict_address():
    address_dict = {'cn-beijing-6': {}, "cn-shanghai-2": {}}
    for region in region_list:
        address = instance_id_name('eip', region, **query_address)
        addressset = address["AddressesSet"]
        for add in addressset:
            allocationid = add.get("AllocationId")
            instanceid = add.get("InstanceId")
            if instanceid:
                address_dict[region].update({allocationid: instanceid})
    return address_dict


query_monitor = {
                'Action': 'GetMetricStatistics',
                'Version': '2010-05-25',
                'Namespace': 'eip',
                'MetricName': 'eip.bps.out',
                # 'StartTime': StartTime,
                # 'EndTime': EndTime,
                'Aggregate': 'Sum',
                'Period': 3600
                }


# 同步金山云昨天的流量
def ksy_yesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    result = 0
    sum_list = []
    # 获取id，name
    dict_instan = dict_instance()

    StartTime = '%sT01:00:00Z' % yesterday
    EndTime = '%sT00:00:00Z' % today
    query_monitor.update({'StartTime': StartTime, 'EndTime': EndTime})

    # 遍历region
    for region in region_list:
        #InstanceId和AllocationId
        address = dict_address()
        for allocation, instance in address[region].items():
            query_monitor.update({"InstanceID": allocation})
            #所有环境的云监控信息
            monitor_date = instance_id_name('monitor', region, **query_monitor)
            member = monitor_date["getMetricStatisticsResult"]["datapoints"]["member"]
            #遍历member中的所有timestamp和sum
            for ts in member:
                sum = ts.get("sum")
                result += int(sum)
            allocation_id = allocation
            instance_name = dict_instan.get(instance, "")
            if instance_name:
                name = instance_name.split("-")
                try:
                    instance_name = name[0]+'-'+name[2]
                except:
                    pass
                sum_dict = {"date": yesterday,
                            "sum": result/1024/1024,
                            "allocation_id": allocation_id,
                            "cloud": 0,
                            "grid_name": instance_name}
                sum_list.append(KsyAliCloud(**sum_dict))
        ret = KsyAliCloud.objects.bulk_create(sum_list)

    return ret


# 获取指定日期内的金山云流量（左闭右开）
# StartTime: 2018-06-01
# EndTime    2018-06-10
def assign_date(start_time, end_time):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    result = 0
    sum_list = []
    # 获取id，name
    dict_instan = dict_instance()
    StartTime = '%sT01:00:00Z' % start_time
    EndTime = '%sT00:00:00Z' % end_time
    query_monitor.update({'StartTime': StartTime, 'EndTime': EndTime})
    # 遍历region
    for region in region_list:
        # InstanceId和AllocationId
        address = dict_address()
        for allocation, instance in address[region].items():
            query_monitor.update({"InstanceID": allocation})
            # 所有环境的云监控信息
            monitor_date = instance_id_name('monitor', region, **query_monitor)
            member = monitor_date["getMetricStatisticsResult"]["datapoints"]["member"]
            allocation_id = allocation
            # 遍历member中的所有timestamp和sum
            for ts in member:
                timestamp = ts.get("timestamp")
                sum = ts.get("sum")
                result += int(sum)
                instance_name = dict_instan.get(instance, "")
                #如果instance_name不为空
                if instance_name:
                    name = instance_name.split("-")
                    instance_name = name[0] + '-' + name[2]
                    #获取一天的数据
                    if str(timestamp)[11:13] == "00":
                        time = datetime.datetime.strptime(timestamp, UTC_FORMAT)
                        r_time = time-oneday
                        timestamp = str(r_time)[0:10]
                        sum_dict = {"date": timestamp,
                                    "sum": result/1024/1024,
                                    "allocation_id": allocation_id,
                                    "cloud": 0,
                                    "grid_name": instance_name}
                        exits = KsyAliCloud.objects.filter(date=sum_dict["date"],
                                                           sum=sum_dict["sum"],
                                                           allocation_id=sum_dict["allocation_id"]).exists()

                        # 避免重复记录
                        if exits == False:
                            sum_list.append(KsyAliCloud(**sum_dict))
                        result = 0
            ret = KsyAliCloud.objects.bulk_create(sum_list)

    return ret


@shared_task
def sync_ksyun():
    logger.info("start sync ksyun data")
    ksy_yesterday()
    logger.info("sync ldap data complete")