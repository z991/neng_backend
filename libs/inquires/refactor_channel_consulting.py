import json
import requests
from ldap_server.configs import GET_PERMIT_URL, GET_DATA_URL
from applications.workorder_manage.models import StationInfo, Grid


class ChannelFetcher(object):
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.grid_data = self.get_grid()

    # 获取grid 的id和grid域名
    def get_grid(self):
        data = []
        res = Grid.objects.all().filter(version_type=2).values('id', 'domain_name')
        for each in res:
            usercenter = eval(each['domain_name']).get('usercenter')
            dolphinsetting = eval(each['domain_name']).get('dolphinsetting')
            if usercenter.startswith('http'):
                data.append({'grid': each['id'], 'usercenter': usercenter,
                             'dolphin': dolphinsetting})
        return data

    # 从重构线上数据库获取siteid
    def get_site_list(self):
        route_list = []
        for each in self.grid_data:
            usercenter_url = each.get('usercenter')
            url = usercenter_url + '/enterprise'
            result = requests.get(url)
            route_info = result.json()

            for item in route_info.get('data'):
                if item.get('enabled') and item['enabled']==1:
                    route_list.append(item['siteid'])
        return route_list

    # 获取user id
    # 说明：遍历site_id 根据siteid去oa找节点，通过节点找到用户中心域名， 访问用户中心找到userid
    # 如果没有在oa找到用户中心的域名  则默认找重构北京(cg-bj)这个节点的域名 在该域名找到userid
    def get_user_id(self):
        site_id_list = self.get_site_list()
        data = []
        for site_id in site_id_list:
            # 'kf_49688'    oa 线上数据库的
            domain_name = StationInfo.objects.all().filter(company_id=site_id, grid__version_type=2)\
                .select_related('grid__domain_name').values_list('grid__domain_name', flat=True)

            if not domain_name:
                continue
            try:
                user_url = eval(domain_name[0]).get('usercenter')
            except:
                pass
            url = f"{user_url}/enterprise/{site_id}/user/1/100"
            result = requests.get(url)
            items = result.json()
            user_dict = {}
            for item in items['data']:
                if item.get('roleid') and ('admin' in item['roleid']) and (item['siteid']==site_id):
                    user_dict['userid'] = item['userid']
                    user_dict['siteid'] = item['siteid']
                    data.append(user_dict)
                    break
        return {'code': '200', 'data': data}

    # 获取许可证
    def get_permit(self):
        user_info = self.get_user_id()
        assert isinstance(user_info, dict)
        data_info = []
        for each in user_info['data']:
            siteid = each.get('siteid')
            userid = each.get('userid')
            url = GET_PERMIT_URL
            data = {"name": "rpt_oa_service",
                    "qry": f"datetime|between|{self.start_time},{self.end_time}&&business|=|{siteid}"}
            headers = {"Content-Type": "application/json", "userid": userid, "siteid": siteid}
            result = requests.put(url=url, data=json.dumps(data), headers=headers)
            items = result.json()
            print('items===', items)
            permit = {}
            if items['state'] == 'starting' and items.get('id'):
                permit['permit'] = items['id']
                permit['siteid'] = siteid
                data_info.append(permit)
        return {'code': '200', 'data': data_info}

    # 获取数据
    def get_data(self):
        permit_info = self.get_permit()
        data = []
        for each in permit_info['data']:
            permit = each.get('permit')
            siteid = each.get('siteid')
            url = GET_DATA_URL + permit
            result = requests.get(url)
            items = result.json()
            if items['state'] == 'ok':
                try:
                    rows = items['result']['rows']
                except:
                    continue
                data.append({'siteid': siteid, 'data': rows})
        return data


def get_site_company():
    data = []
    a = []
    res = Grid.objects.all().filter(version_type=2).values('id', 'domain_name')
    for each in res:
        usercenter = eval(each['domain_name']).get('usercenter')
        dolphinsetting = eval(each['domain_name']).get('dolphinsetting')
        if usercenter.startswith('http'):
            a.append({'grid': each['id'], 'usercenter': usercenter,
                         'dolphin': dolphinsetting})
    for each in a:
        url_ = each.get('usercenter')
        url = url_+"/enterprise"
        result = requests.get(url)
        route_info = result.json()
        data.extend(route_info['data'])
    return data