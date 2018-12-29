import requests
from libs.redis import Redis_base
from multiprocessing import Pool
import datetime
import operator
from ldap_server.configs import MAIN_TJ, key_dict, one_g, m_500, m_300
from ldap_server.database_connect import ZABBIX_PASSWORD, ZABBIX_URL, ZABBIX_USER
from collections import deque


# zabbix类
class ZabbixApi:

    def get_key(self):
        """
        获取密钥
        :return:
        """
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": ZABBIX_USER,
                "password": ZABBIX_PASSWORD
            },
            "id": 0
        }
        res = requests.post(url=ZABBIX_URL, json=data)
        result = res.json()
        key = result.get("result")
        return key

    # 2.获取zabbix所有的主机组
    def get_major_unit(self, auth):
        """
        获取zabbix所有的主机组
        :param auth:
        :return:[{"groupid": "72","name": "bj-ali-ck1000"},{"groupid": "99","name": "bj-ali-jh1000"}]
        """
        major_name = []
        major_groupid = []

        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": ["groupid", "name"]
            },
            "auth": auth,

            "id": 1
        }
        res = requests.post(url=ZABBIX_URL, json=data)
        result = res.json()
        major = result.get("result")
        return major

    # 3.获取单个组下的所有主机
    def get_mainframe(self, auth,groupids):
        """
        获取单个组下的所有主机
        :param auth, groupids:
        :return:[{"hostid": "13398","name": "bj-ali-ck1000-web-01"},{"hostid": "13398","name": "bj-ali-ck1000-web-01"}]
        """
        # key = get_key()
        # if key == None:
        #     return JsonResponse({"error": "获取认证密钥错误"}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "name"],
                "groupids": groupids
            },
            "auth": auth,
            "id": 1
        }
        res = requests.post(url=ZABBIX_URL, json=data)
        result = res.json()
        mainframe = result.get("result")
        return mainframe

    # 4.获取某个主机下的指定监控项
    def get_main_monitor(self, auth, hostids, key_, group_name, main_name):
        """
        获取某个主机下的指定监控项
        :param auth, hostids, key_:
        :return: {"itemid": "260129","lastvalue": "76462063616"}
        """
        data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["lastvalue"],
                "hostids": hostids,
                "search": {
                    "key_": key_
                },
                "sortfield": "name"
            },
            "auth": auth,
            "id": 1
        }
        res = requests.post(url=ZABBIX_URL, json=data)
        result = res.json()
        if result["result"] == []:
            lastvalue = 0
        else:
            lastvalue = result["result"][0].get("lastvalue", 0)

        za_dict = {"group_name": group_name, "host_name": main_name, "key": key_, "lastvalue": lastvalue}
        return za_dict


memory_dict = {}
class CheckoutResult:
    # CPU等待
    # 小于10正常，大于30告警，大于50灾难
    #
    # 内存可使用
    # 大于500M
    # 正常
    # 小于500M
    # 告警
    # 最近3次中 小于300M 大于2次 灾难
    #
    # 系统负载
    # 小于4
    # 正常
    # 大于4
    # 告警
    # 大于8
    # 灾难

    # 校验内存
    def memory(self, ma_k, m):
        if int(m) >= m_500 or int(m) == 0:
            statu = 1
        elif int(m) < m_500 and int(m) > m_300:
            statu = 2
        elif int(m) < m_300 and int(m) > 0:
            statu = 3

        deq = deque(maxlen=3)
        if ma_k not in memory_dict:
            memory_dict[ma_k] = deq
            memory_dict[ma_k].append(statu)
        else:
            memory_dict[ma_k].append(statu)

        deq_res = memory_dict[ma_k]
        res_count = deq_res.count(3)
        res_last = deq_res[-1]

        if res_count > 2:
            status = 3
            massage = "内存不足"
        elif res_count < 3 and res_last == 2:
            status = 2
            massage = "内存不足"
        else:
            status = 1
            massage = ""
        return status, massage

    # 校验磁盘
    def disk(self,opt_free, fs_free, opt_total, fs_total):
        if int(opt_total) == 0 or int(fs_total) == 0:
            status = 1
            massage = ""
        elif opt_total != 0 and fs_total != 0:
            opt = int(opt_free) / int(opt_total)
            fs = int(fs_free) / int(fs_total)

            if opt >= 0.2 or fs >= 0.2:
                status = 1
                massage = ""
            elif (opt < 0.2 and opt > 0.1) or (fs < 0.2 and fs > 0.1):
                status = 2
                massage = "磁盘不足"
            elif opt < 0.1 or fs < 0.1:
                status = 3
                massage = "磁盘不足"

        return status, massage

    # cpu使用
    # def cpu_use(self, use):
    #     if eval(use) >= 50 or use == 0:
    #         status = 1
    #         massage = ""
    #     elif float(use) < 50 and float(use) > 40:
    #         status = 2
    #         massage = "CPU超载"
    #     elif float(use) <= 40:
    #         status = 3
    #         massage = "CPU超载"
    #     return status, massage

    # cpu等待
    def cpu_waite(self, waite):
        if float(waite) <= 30 or waite == 0:
            status = 1
            massage = ""
        elif float(waite) > 30 and float(waite) <= 50:
            status = 2
            massage = "CPU等待"
        elif float(waite) > 50:
            status = 3
            massage = "CPU等待"
        return status, massage

    # 负载from multiprocessing import current_process
    def cpu_load(self, load):
        if float(load) <= 4 or load == 0:
            status = 1
            massage = ""
        elif float(load) > 4 and float(load) <= 8:
            status = 2
            massage = "系统超载"
        elif float(load) > 8:
            status = 3
            massage = "系统超载"
        return status, massage


def grid_monitor():
    checkout = CheckoutResult()
    zabbix = ZabbixApi()
    # 获取密钥
    auth = ZabbixApi().get_key()

    # 获取所有主机组
    major= zabbix.get_major_unit(auth)
    # 创建进程池
    pp_memory_available = Pool(8)

    li = []
    for m in major:
        group_id = m["groupid"]
        group_name = m["name"]
        if group_name[0:2] in MAIN_TJ:
            # 某个主机组下的所有主机
            mainframe = zabbix.get_mainframe(auth, group_id)
        else:
            continue
        if mainframe == []:
            continue
        # 遍历所有的主机
        for main in mainframe:
            hostid = main["hostid"]
            main_name = main["name"]

            memory_available = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "vm.memory.size[available]", group_name, main_name))
            # cpu_idle = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "system.cpu.util[,idle]", group_name, main_name))
            cpu_iowait = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "system.cpu.util[,iowait]", group_name, main_name))
            cpu_loda = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "system.cpu.load[percpu,avg1]", group_name, main_name))
            opt_free = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "vfs.fs.size[/opt,free]", group_name, main_name))
            fs_free = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "vfs.fs.size[/,free]", group_name, main_name))
            opt_total = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "vfs.fs.size[/opt,total]", group_name, main_name))
            fs_total = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "vfs.fs.size[/,total]", group_name, main_name))
            li.extend([memory_available, cpu_iowait, cpu_loda, opt_free, fs_free, opt_total, fs_total])

    # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    pp_memory_available.close()
    pp_memory_available.join()

    pp_result = {}

    for item in li:
        l = item.get()
        # ll.get()获取的数据结构
        # {'group_name': '北京轨迹集群', 'host_name': 'bj-ksy-g1-traildb_master-01', 'key': 'vfs.fs.size[/,total]', 'lastvalue': '19549736960'}
        group_name = l["group_name"]
        host_name = l["host_name"]
        key_ = l["key"]
        key = key_dict[key_]
        lastvalue = l["lastvalue"]

        if group_name not in pp_result:
            pp_result[group_name] = {host_name: {key: lastvalue}}
        elif host_name not in pp_result[group_name]:
            pp_result[group_name].update({host_name: {key: lastvalue}})
        else:
            pp_result[group_name][host_name].update({key: lastvalue})
    result = []
    look_list=[]
    # 遍历所有主机组
    for p_k, p_v in pp_result.items():
        s_set = set()
        m_set = set()
        members_list = []
        for ma_k, ma_v in p_v.items():
            memory_available = ma_v["系统可用内存"]
            # cpu_idle = ma_v["cpu可用使用率"]
            cpu_iowait = ma_v["cpu等待"]
            cpu_loda = ma_v["一分钟负载"]
            opt_free = ma_v["opt可用"]
            fs_free = ma_v["根可用"]
            opt_total = ma_v["opt总容量"]
            fs_total = ma_v["根总容量"]
            if 0 < int(memory_available) <= m_300:
                look_list.append({ma_k: memory_available})

            m_status, m_massage = checkout.memory(ma_k, memory_available)
            if m_status != 1:
                s_set.add(m_status)
                m_set.add(m_massage)
            # i_status, i_massage = checkout.cpu_use(cpu_idle)
            # if i_status != 1:
            #     s_set.add(i_status)
            #     m_set.add(i_massage)
            w_status, w_massage = checkout.cpu_waite(cpu_iowait)
            if w_status != 1:
                s_set.add(w_status)
                m_set.add(w_massage)
            l_status, l_massage = checkout.cpu_load(cpu_loda)
            if l_status != 1:
                s_set.add(l_status)
                m_set.add(l_massage)
            d_status, d_massage = checkout.disk(opt_free, fs_free, opt_total, fs_total)
            if d_status != 1:
                s_set.add(d_status)
                m_set.add(d_massage)

        m_list = list(m_set)

        if len(m_list) == 0:
            m_list = ["正常"]

        s_list = list(s_set)
        if len(s_list) == 0:
            statu = 1
        else:
            st = sorted(s_list)
            statu = st[-1]
        date = datetime.datetime.now().strftime('%m-%d %H:%M')

        if statu != 1:
            members_list.append({"ma_k": ma_k, "status": statu, })
            result.append({"group_name": p_k, "status": statu, "massage": m_list, "date": date})
        else:
            continue
    sorted_x = sorted(result, key=operator.itemgetter('status'), reverse=True)
    Redis_base().set("zabbix_zxy", sorted_x)
    return '存储ok'


def xg_grid_monitor():
    checkout = CheckoutResult()
    zabbix = ZabbixApi()
    # 获取密钥
    auth = ZabbixApi().get_key()

    # 获取所有主机组
    major = zabbix.get_major_unit(auth)
    # 创建进程池
    pp_memory_available = Pool(8)

    li = []
    for m in major:
        group_id = m["groupid"]
        group_name = m["name"]
        if group_name[0:2] in MAIN_TJ:
            # 某个主机组下的所有主机
            mainframe = zabbix.get_mainframe(auth, group_id)
        else:
            continue
        if mainframe == []:
            continue
        # 遍历所有的主机
        for main in mainframe:
            hostid = main["hostid"]
            main_name = main["name"]

            memory_available = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(
            auth, hostid, "vm.memory.size[available]", group_name, main_name))
            # cpu_idle = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(auth,hostid, "system.cpu.util[,idle]", group_name, main_name))
            cpu_iowait = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(
            auth, hostid, "system.cpu.util[,iowait]", group_name, main_name))
            cpu_loda = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(
            auth, hostid, "system.cpu.load[percpu,avg1]", group_name, main_name))
            opt_free = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(
            auth, hostid, "vfs.fs.size[/opt,free]", group_name, main_name))
            fs_free = pp_memory_available.apply_async(zabbix.get_main_monitor,
                                                      args=(auth, hostid, "vfs.fs.size[/,free]", group_name, main_name))
            opt_total = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(
            auth, hostid, "vfs.fs.size[/opt,total]", group_name, main_name))
            fs_total = pp_memory_available.apply_async(zabbix.get_main_monitor, args=(
            auth, hostid, "vfs.fs.size[/,total]", group_name, main_name))
            li.extend([memory_available, cpu_iowait, cpu_loda, opt_free, fs_free, opt_total, fs_total])

    # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    pp_memory_available.close()
    pp_memory_available.join()

    pp_result = {}

    for item in li:
        l = item.get()
        # ll.get()获取的数据结构
        # {'group_name': '北京轨迹集群', 'host_name': 'bj-ksy-g1-traildb_master-01', 'key': 'vfs.fs.size[/,total]', 'lastvalue': '19549736960'}
        group_name = l["group_name"]
        host_name = l["host_name"]
        key_ = l["key"]
        key = key_dict[key_]
        lastvalue = l["lastvalue"]

        if group_name not in pp_result:
            pp_result[group_name] = {host_name: {key: lastvalue}}
        elif host_name not in pp_result[group_name]:
            pp_result[group_name].update({host_name: {key: lastvalue}})
        else:
            pp_result[group_name][host_name].update({key: lastvalue})
    result = []
    look_list = []
    # 遍历所有主机组
    for p_k, p_v in pp_result.items():
        # 一个主机组下的非正常主机信息列表
        group_list = []
        s_set = set()
        m_set = set()
        members_list = []
        for ma_k, ma_v in p_v.items():
            # 存放非正常的状态和信息的列表
            ma_list = []
            memory_available = ma_v["系统可用内存"]
            # cpu_idle = ma_v["cpu可用使用率"]
            cpu_iowait = ma_v["cpu等待"]
            cpu_loda = ma_v["一分钟负载"]
            opt_free = ma_v["opt可用"]
            fs_free = ma_v["根可用"]
            opt_total = ma_v["opt总容量"]
            fs_total = ma_v["根总容量"]

            m_status, m_massage = checkout.memory(ma_k, memory_available)
            if m_status != 1:
                ma_list.append({"status": m_status, "massage": m_massage})
                s_set.add(m_status)
                m_set.add(m_massage)
            # i_status, i_massage = checkout.cpu_use(cpu_idle)
            # if i_status != 1:
            #     s_set.add(i_status)
            #     m_set.add(i_massage)
            w_status, w_massage = checkout.cpu_waite(cpu_iowait)
            if w_status != 1:
                ma_list.append({"status": w_status, "massage": w_massage})
                s_set.add(w_status)
                m_set.add(w_massage)

            l_status, l_massage = checkout.cpu_load(cpu_loda)
            if l_status != 1:
                ma_list.append({"status": l_status, "massage": l_massage})
                s_set.add(l_status)
                m_set.add(l_massage)
            d_status, d_massage = checkout.disk(opt_free, fs_free, opt_total, fs_total)
            if d_status != 1:
                ma_list.append({"status": d_status, "massage": d_massage})
                s_set.add(d_status)
                m_set.add(d_massage)
            # 一个主机的所有报警信息
            ma_dict = {"ma_k": ma_k, "st_me": ma_list}
            if len(ma_list) > 0:
                group_list.append(ma_dict)
            else:
                continue

        m_list = list(m_set)

        if len(m_list) == 0:
            m_list = ["正常"]

        s_list = list(s_set)
        if len(s_list) == 0:
            statu = 1
        else:
            st = sorted(s_list)
            statu = st[-1]
        date = datetime.datetime.now().strftime('%m-%d %H:%M')

        if statu != 1:
            result.append({"group_name": p_k, "status": statu, "massage": m_list, "date": date, "member": group_list})
        else:
            continue
    sorted_x = sorted(result, key=operator.itemgetter('status'), reverse=True)
    Redis_base().set("zabbix_zxy", sorted_x)
    return '存储ok'