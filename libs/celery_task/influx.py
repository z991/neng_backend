from influxdb import InfluxDBClient
from ldap_server.database_connect import INFLUX_HOST, INFLUX_NAME, INFLUX_PASSWORD, INFLUX_PORT, INFLUX_USER
from ldap_server.configs import HOST_DICT
from libs.redis import Redis_base


class InfluxDb(object):
    def get_database(self):
        """
        连接数据库查询
        :return:
        """
        influx_host = INFLUX_HOST
        influx_port = INFLUX_PORT
        influx_user = INFLUX_USER
        influx_password = INFLUX_PASSWORD
        influx_database = INFLUX_NAME
        client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_database)
        return client

    # 查询数据库获取host和url
    def get_host_url(self):
        data = []
        network = []
        client = self.get_database()
        host_sql = "select average_response_ms from autogen.ping " \
                   "where url='bj-p1-slb4t2dmqtt' group by host, url order by time desc limit 1"
        url_sql = "select average_response_ms from autogen.ping " \
                  "where host='bj-ksy-v0-network-01' group by host, url order by time desc limit 1"

        host = client.query(host_sql)
        url = client.query(url_sql)

        host_dict = {}
        url_list = []

        for table_name, host_value in host.keys():
            if not HOST_DICT.get(host_value.get('host')):
                continue
            host_dict[host_value.get('host')] = HOST_DICT[host_value.get('host')]

        for table_name, url_value in url.keys():
            url_list.append(url_value.get('url'))

        for j in url_list:
            network.append({'name': j})
            for i in host_dict.keys():
                data.append((i, j))
        return data, network, host_dict

    # 查询数据库获取延迟和丢包率
    def get_network_ms(self):
        client = self.get_database()
        data, network, host_dict = self.get_host_url()
        result_data = []
        for host, url in data:
            network_sql = "select average_response_ms, percent_packet_loss from autogen.ping " \
                          "where host='%s' and url='%s' order by time desc limit 1;" % (host, url)
            result = client.query(network_sql)
            if result:
                for value in result:
                    ms = value[0].get('average_response_ms')
                    loss = value[0].get('percent_packet_loss')
                    result_data.append({'host': host, 'url': url, 'ms': ms, 'loss': loss})

        # Redis_base().set("network_yzq", network)
        return result_data, host_dict

    # 解析数据
    def parse_ms_loss(self):
        result_data, host_dict = self.get_network_ms()
        network = []
        packet = []
        url_dict = {}
        for item in result_data:
            url_value = item.get('url')
            host_value = item.get('host')
            ms = item.get('ms')
            loss = item.get('loss')
            if url_dict.get(url_value):
                url_dict[url_value][host_value] = [ms, loss]
            else:
                url_dict[url_value] = {host_value: [ms, loss]}

        for url, each in url_dict.items():
            inner_dict_ms = {'name': url}
            inner_dict_loss = {'name': url}
            for value, inner_each in each.items():
                inner_dict_ms[value] = inner_each[0]
                inner_dict_loss[value] = inner_each[1]

            network.append(inner_dict_ms)
            packet.append(inner_dict_loss)

        # 按规则收敛
        packet = self.constriction_loss(packet, host_dict)
        network = self.constriction_ms(network, host_dict)

        packet = self.parse_dict(packet)
        network = self.parse_dict(network)
        host_dict = self.parse_dict(host_dict)

        Redis_base().set("network_yzq", network)
        Redis_base().set("packet_yzq", packet)
        Redis_base().set("title_yzq", host_dict)
        return network, packet, host_dict

    # 丢包收敛规则
    def constriction_loss(self, data, host_dict):
        # 丢包率：网络丢包 正常<=0% 告警>=0% 灾难 >=10%
        for item in data:
            for each in host_dict.keys():
                value = item.get(each, '0')
                value = str(value)
                if '%' in value:
                    number = int(value.strip("%"))/100
                    if 0<number<0.1:
                        item[each] = str(value)+'Y'
                    elif number>0.1:
                        item[each] = str(value)+'R'

                else:
                    item[each] = 0

        return data

    # 延迟收敛规则
    def constriction_ms(self, data, host_dict):
        # 延迟： 网络延迟 正常<=60ms 60ms<告警<=70ms 灾难>=70ms
        for item in data:
            for each in host_dict.keys():
                value = item.get(each, 0)
                if value:
                    if 60<value<=70:
                        item[each] = str(value)+'Y'
                    elif value>70:
                        item[each] = str(value)+'R'
                else:
                    item[each] = 0
        return data

    def parse_dict(self, data):
        initial = {
            "sz-ksy-v0-network-01": "szbgp",
            "sh-ksy-v0-network-02": "shlt",
            "sh-ksy-v0-network-01": "shdx",
            "hz-ali-g1-zabbix_proxy-01": "hzbgp",
            "bj-ksy-v0-network-02": "bjlt",
            "bj-ksy-v0-network-01": "bjdx",
            "bj-ali-g1-zabbix_proxy-01": "bjbgp"
        }
        if isinstance(data, list):
            for item in data:
                for key in initial.keys():
                    if key in item.keys():
                        item[initial[key]] = item.pop(key)
        if isinstance(data, dict):
            for key in initial.keys():
                if key in data.keys():
                    data[initial[key]] = data.pop(key)
        return data
