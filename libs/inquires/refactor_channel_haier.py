import psycopg2
import requests
from applications.workorder_manage.models import Grid
from libs.datetimes import datetime_delta, str_to_date, date_to_str
from ldap_server.database_connect import REFACTOR_HOST, REFACTOR_NAME, REFACTOR_PASSWORD, REFACTOR_PORT, \
    REFACTOR_USER


class ChannelFetcherHaiEr(object):
    """
    获取重构咨询量和访客的类
    1. 在生态云商找到grid 并且找到每个grid的域名
    2. 根据域名找到每个grid下的站点（siteid）
    3. 连接重构数据库 遍历每个siteid 查询访客量和咨询量
    """
    def __init__(self, start_time):
        self.start_time = str(start_time) + ' 00:00:00'
        self.end_time = date_to_str(datetime_delta(str_to_date(start_time), days=1)) + ' 00:00:00'
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

    # 获取重构数据库连接
    def get_conn(self):
        cg_host = REFACTOR_HOST
        cg_port = REFACTOR_PORT
        cg_user = REFACTOR_USER
        cg_password = REFACTOR_PASSWORD
        cg_database = REFACTOR_NAME
        conn = psycopg2.connect(database=cg_database, user=cg_user, password=cg_password,
                                host=cg_host, port=cg_port)
        return conn

    # 执行sql
    def query_sql(self, sql, cur):
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    # 获取数据
    def get_data(self):

        site_list = self.get_site_list()
        conn = self.get_conn()
        cur = conn.cursor()
        # 访客量查询
        vis_sql = f"SELECT tml,count(*), event_siteid FROM ods_nl_pv_alone " \
                  f"WHERE event_time>='{self.start_time}' " \
                  f"AND event_time<'{self.end_time}' GROUP BY tml, event_siteid"

        # 咨询量查询
        con_sql = f"select client, sum(consult_valid_count), sum(consult_invalid_count), siteid " \
                  f"from ph_ns_client_sum where act_time>='{self.start_time}' and act_time<'{self.end_time}'" \
                  f" group by client, siteid"

        vis_dict = self.query_sql(vis_sql, cur)
        con_dict = self.query_sql(con_sql, cur)

        data = {'siteid': site_list, 'vis': vis_dict, 'con': con_dict}
        # conn.commit()
        cur.close()
        conn.close()
        return data
