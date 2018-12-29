from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User

from libs.datetimes import str_to_date, datetime_delta, date_to_str
from applications.log_manage.models import OperateLog, DetailLog
from .serializers import OperateLogSerializer, PersonalLogSerializer
from rest_framework.decorators import detail_route, list_route, api_view
from applications.log_manage.log_dict import openstation_dict, get_product, operation_type, log_str_change, khk_num, \
    matter_word, version_dict
from applications.workorder_manage.models import AreaInfo, Matter, Reject, ProductConfig, StationInfo
from ldap_server.configs import ACTION_MAP, FUNCTION_SELECT, MATTER_STATUS, TRAINING_METTART_METHOD, PRODUCT_STATUS


# Create your views here.
class SystemLogViewSet(viewsets.ModelViewSet):
    queryset = OperateLog.objects.all().exclude(operationmodule__in=("客户库", "培训管理"))
    serializer_class = OperateLogSerializer

    def get_queryset(self):
        kwargs = self.request.GET
        query_params = {}
        from_date = kwargs.get("form_date", None)
        to_date = kwargs.get("to_date", None)
        username = kwargs.get("username", None)
        operationmodule = kwargs.get("name", None)
        if from_date:
            query_params.update({"operationtime__gte": str_to_date(from_date)})
        if to_date:
            to_date = datetime_delta(str_to_date(to_date), days=1)
            query_params.update({"operationtime__lte": to_date})
        if username:
            query_params.update({"user__last_name__icontains": username})
        if operationmodule:
            query_params.update({"operationmodule": operationmodule})
        return OperateLog.objects.all().filter(**query_params).exclude(operationmodule__in=("客户库", "培训管理")).order_by("-operationtime")

    def check_permissions(self, request):
        super(SystemLogViewSet, self).check_permissions(request)
        if not request.user.has_perm("log_manage.view_system-log"):
            self.permission_denied(request)

    @list_route(['GET'])
    def operation_type(self, request):
        data = operation_type
        return Response(data=data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def get_detail(self, request, pk=None, *args, **kwargs):
        """
        日志详情接口
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = DetailLog.objects.filter(log_id=pk)
        data = []
        for q in queryset:
            value_dict = {
                "name": q.name,
                "old_value": q.old_value,
                "new_value": q.new_value
            }
            data.append(value_dict)
        return Response(data=data, status=status.HTTP_200_OK)


class PersonalLogViewSet(viewsets.ModelViewSet):
    queryset = OperateLog.objects.all().exclude(operationmodule__in=("客户库", "培训管理"))
    serializer_class = PersonalLogSerializer

    def get_queryset(self):
        kwargs = self.request.GET
        query_params = {"user_id": self.request.user.id}
        from_date = kwargs.get("form_date", '').strip()
        to_date = kwargs.get("to_date", '').strip()
        operationmodule = kwargs.get("name", None)
        if from_date and from_date != 'undefined':
            query_params.update({"operationtime__gte": str_to_date(from_date)})
        if to_date and to_date != 'undefined':
            to_date = datetime_delta(str_to_date(to_date), days=1)
            query_params.update({"operationtime__lte": to_date})
        if operationmodule:
            query_params.update({"operationmodule": operationmodule})
        return OperateLog.objects.all().filter(**query_params).exclude(operationmodule__in=("客户库", "培训管理")).order_by("-operationtime")


class OpenStationViewSet(viewsets.ModelViewSet):
    """
    开站修改日志记录
    """
    queryset = OperateLog.objects.all()

    def __init__(self):
        self.open_list = []

    @classmethod
    def create_base_log(self, request, title, operationmodule, action):
        """
        创建基础日志
        :param request:
        :return:
        """
        ip = OperateLog.get_remote_ip(request)
        user = request.user

        operate_dict = {
            "ip": ip,
            "user": user,
            "action": action,
            "operationmodule": operationmodule,
            "title": title
        }
        ret = OperateLog.objects.create(**operate_dict)
        return ret

    # 获取初始数据&数据入库
    @list_route(['POST'])
    def put_detail(self, request):
        """
        获取数据
        :param request:
        :return:
        """
        data = request.data

        # 旧数据
        old_date = data.get("old_date")
        # 旧company_info数据
        old_company = old_date.get("company_info")
        # 旧link_info数据
        old_link_info = old_date.get("link_info")
        # 旧station_info数据
        old_station = old_date.get("station_info")
        # 旧account_info数据
        old_account = old_date.get("account_conf")
        # 新数据
        new_date = data.get("new_date")
        # 修改后的公司信息
        company = new_date.get("company_info")
        # 修改后的联系人信息
        link_info = new_date.get("link_info")
        # 修改后的站点信息
        stations = new_date.get("station_info")
        # 账户信息
        account = new_date.get("account_conf")
        # 功能开关修改信息(由前端整理后直接传过来的)
        func_list = new_date.get("func_list")
        company_id = stations.get("company_id")

        action = ACTION_MAP["PUT"]
        # 新增基础日志信息
        log_id = self.create_base_log(request, company_id, "开站管理", action)
        # 比对企业信息是否有修改
        self.diff_company(old_company, company, log_id)
        # 比对站点信息是否有修改
        self.diff_station(old_station, stations, log_id)
        # 比对联系人信息是否有修改
        self.diff_link(old_link_info, link_info, log_id)
        # 比对账户信息是否有修改
        self.diff_account(old_account, account, log_id)
        # 获取功能开关的变化
        open_list = self.diff_func(func_list, log_id)
        DetailLog.objects.bulk_create(open_list)

        return Response(status=status.HTTP_200_OK)

    @list_route(['POST'])
    def khk_put(self, request):
        data = request.data
        m_list = []
        # 操作模块
        operationmodule = data.get("operationmodule")
        # 客户id
        title = data.get("title")
        # 修改变化列表
        modify_list = data.get("modify_list")
        action = ACTION_MAP['PUT']
        # 创建基础日志
        log_id = self.create_base_log(request, title, operationmodule, action)

        for i in modify_list:
            word = i["word"]
            if word in openstation_dict:
                name = openstation_dict[word]
            else:
                name = word
            # 附件原值
            if word == "contract_accessory":
                old = i["old_value"]
                new = i["new_value"]
                if old == "":
                    i["old_value"] = ""
                    new_list = []
                    for n in eval(new):
                        new_list.append(n["name"])
                    i["new_value"] = new_list
                elif new == "[]":
                    old_list = []
                    for o in eval(old):
                        old_list.append(o["name"])
                    i["old_value"] = old_list
                    i["new_value"] = ""
                else:
                    old_list = []
                    new_list = []
                    for o in eval(old):
                        old_list.append(o["name"])
                    for n in eval(new):
                        new_list.append(n["name"])
                    i["old_value"] = old_list
                    i["new_value"] = new_list

            # 判断公司地址
            if word == "company_address":
                old_d = i["old_value"]
                new_d = i["new_value"]
                old_province = old_d.get("province")
                old_city = old_d.get("city")
                detail = old_d.get("detail")
                new_provinece = AreaInfo.objects.get(pk=new_d.get("province")).atitle
                new_city = AreaInfo.objects.get(pk=new_d.get("city")).atitle
                new_detail = new_d.get("detail")
                if old_province == "":
                    i["old_value"] = ""
                else:
                    province = AreaInfo.objects.get(pk=old_province).atitle
                    city = AreaInfo.objects.get(pk=old_city).atitle
                    i["old_value"] = province + city + detail
                i["new_value"] = new_provinece + new_city + new_detail
            i.update({"log_id": log_id, "name": name})
            # 对值是数字的进行类型转换
            if word in khk_num:
                i["old_value"] = khk_num[word][i["old_value"]]
                i["new_value"] = khk_num[word][i["new_value"]]
            m_list.append(DetailLog(**i))
        ret = DetailLog.objects.bulk_create(m_list)
        return Response(data={"info": "修改操作记录成功"}, status=status.HTTP_200_OK)

    @list_route(['POST'])
    def khk_hd(self, request):
        data = request.data
        # 旧数据
        old_date = data.get("old_date")
        # 旧company_info数据
        old_company = old_date.get("company_info")
        # 旧link_info数据
        old_link_info = old_date.get("link_info")
        # 旧order_info数据
        old_order = old_date.get("order_info")
        # 旧function_info数据
        old_function = old_date.get("function_info")

        # 新数据
        new_date = data.get("new_date")
        # 修改后的公司信息
        company = new_date.get("company_info")
        # 修改后的联系人信息
        link_info = new_date.get("link_info")
        # 修改后的order_info
        order_info = new_date.get("order_info")
        # function_info数据账户信息
        function_info = new_date.get("function_info")

        title = old_date["id"]
        log_id = self.create_base_log(request,title, "客户库", 3)
        # 比对企业信息是否有修改
        self.diff_company(old_company, company, log_id)
        # 比对联系人信息
        self.diff_link(old_link_info, link_info, log_id)
        self.diff_order_info(old_order, order_info, log_id)
        open_list = self.diff_funckhk(old_function, function_info, log_id)
        DetailLog.objects.bulk_create(open_list)
        return Response(status=status.HTTP_200_OK)

    def diff_company(self, old_company, company, log_id):
        """
        比较公司信息
        :param old_company:
        :param company:
        :return:
        """
        for c, v in old_company.items():
            # 判断url
            if c == "company_url":
                self.diff_url(old_company["company_url"], company["company_url"], log_id)
            # 判断地址
            elif c == "company_address":
                self.diff_address(old_company["company_address"], company["company_address"], log_id)
            elif company[c] != v:
                com_dict = {
                    "word": c,
                    "name": openstation_dict[c],
                    "new_value": company[c],
                    "old_value": v,
                    "log_id": log_id
                }
                self.open_list.append(DetailLog(**com_dict))
        return self.open_list

    def diff_url(self, old_url, url, log_id):
        """
        比较url
        :param old_url:
        :param url:
        :return:
        """
        if old_url != url:
            url_dict = {
                "word": "company_url",
                "name": "公司url",
                "new_value": url,
                "old_value": old_url,
                "log_id": log_id,
            }
            self.open_list.append(DetailLog(**url_dict))
        else:
            pass
        return self.open_list

    def diff_address(self, old_address, address, log_id):
        """
        比较
        :param old_address:
        :param address:
        :return:
        """
        if old_address != address:
            if old_address != None:
                old_p = AreaInfo.objects.get(pk=old_address.get("province")).atitle
                old_c = AreaInfo.objects.get(pk=old_address.get("city")).atitle
            else:
                old_p, old_c, old_d = "无", "无", "无"
            new_p = AreaInfo.objects.get(pk=address["province"]).atitle
            new_c = AreaInfo.objects.get(pk=address["city"]).atitle
            address_dict = {
                "word": "company_address",
                "name": "公司详细地址",
                "new_value": new_p+new_c+address.get("detail"),
                "old_value": old_p+old_c+old_d,
                "log_id": log_id,
            }
            self.open_list.append(DetailLog(**address_dict))
        else:
            pass
        return self.open_list

    def diff_station(self, old_station, stations, log_id):
        """
        比较站点
        :param old_station:
        :param stations:
        :return:
        """
        for s, v in old_station.items():
            if s == "pact_products":
                self.diff_product(old_station["pact_products"], stations["pact_products"], log_id)
            elif stations[s] != v:
                stations_dict = {
                    "word": s,
                    "name": openstation_dict[s],
                    "new_value": stations[s],
                    "old_value": v,
                    "log_id": log_id
                }
                self.open_list.append(DetailLog(**stations_dict))

        return self.open_list

    def diff_product(self, old_product, product, log_id):
        """
        比较产品
        :param old_product:
        :param product:
        :return:
        """
        if old_product != product:
            old_list = []
            new_list = []
            product_dict = get_product()
            for old_p in old_product:
                old_list.append(product_dict[old_p])
            for new_p in product:
                new_list.append(product_dict[new_p])
            pact_dict ={
                "word": "pact_products",
                "name": "合同产品",
                "new_value": new_list,
                "old_value": old_list,
                "log_id": log_id,
            }
            self.open_list.append(DetailLog(**pact_dict))
        else:
            pass
        return self.open_list

    def diff_link(self, old_link, link, log_id):
        """
        比较联系人信息
        :param old_lind:
        :param link:
        :return:
        """
        if old_link != link:
            link_dict = {
                "word": "link_info",
                "name": "联系人信息",
                "new_value": link,
                "old_value": old_link,
                "log_id": log_id
            }
            self.open_list.append(DetailLog(**link_dict))
        else:
            pass
        return self.open_list

    def diff_account(self, old_account, account, log_id):
        """
        比较账户
        :param old_account:
        :param account:
        :return:
        """
        for a, v in old_account[0].items():
            if account[0][a] != v:
                account_dict = {
                    "word": a,
                    "name": openstation_dict[a],
                    "old_value": v,
                    "new_value": account[0][a],
                    "log_id": log_id
                }
                self.open_list.append(DetailLog(**account_dict))
            else:
                pass
        return self.open_list

    def diff_func(self, func_list, log_id):
        """
        获取功能开关更改信息
        :param func_list:
        :param log_id:
        :return:
        """
        for f in func_list:
            f.update({"log_id": log_id})
            self.open_list.append(DetailLog(**f))
        return self.open_list

    def diff_contract(self, old_list, new_list):
        old_values = []
        new_values = []
        contract_dict = dict(FUNCTION_SELECT)
        if old_list != new_list:
            for o in old_list:
                old_values.append(contract_dict[o])
            for n in new_list:
                new_values.append(contract_dict[n])
        return old_values, new_values

    def diff_order_info(self, old_order, order_info, log_id):
        """
        比较order_info
        :param old_station:
        :param stations:
        :return:
        """
        for s, v in order_info.items():
            if order_info[s] != v:
                stations_dict = {
                    "word": s,
                    "name": openstation_dict[s],
                    "new_value": order_info[s],
                    "old_value": v,
                    "log_id": log_id
                }
                self.open_list.append(DetailLog(**stations_dict))

        return self.open_list

    def diff_funckhk(self, old_func, func_info, log_id):
        old_values = []
        new_values = []
        contract_dict = dict(FUNCTION_SELECT)
        if old_func != func_info:
            for o in old_func:
                old_values.append(contract_dict[o])
            for n in func_info:
                new_values.append(contract_dict[n])
            func_dict = {
                "word": "contract",
                "name": "合同产品",
                "old_value": old_values,
                "new_value": new_values,
                "log_id": log_id
            }
            self.open_list.append(DetailLog(**func_dict))
        else:
            pass
        return self.open_list


class UnifyLog(viewsets.ModelViewSet):
    queryset = OperateLog.objects.all()

    @list_route(['POST'])
    def unify_put(self, request):
        data = request.data
        m_list = []
        # 操作模块
        operationmodule = data.get("operationmodule")
        # 操作对象唯一标识
        title = data.get("title")
        # 修改变化列表
        modify_list = data.get("modify_list")
        action = ACTION_MAP['PUT']
        # 创建基础日志
        log_id = OpenStationViewSet.create_base_log(request, title, operationmodule, action)
        for i in modify_list:
           i.update({"log_id": log_id})
           m_list.append(DetailLog(**i))
        ret = DetailLog.objects.bulk_create(m_list)
        return Response(data={"info": "修改操作记录成功"}, status=status.HTTP_200_OK)

    @list_route(['POST'])
    def unify_delete(self, request):
        """
        删除记录操作
        :param request:
        :return:
        """
        data = request.data
        # 操作模块
        operationmodule = data.get("operationmodule")
        # 操作对象唯一标识
        title = data.get("title")
        # 动作
        action = data.get("action")
        # 创建基础日志
        base_log = OpenStationViewSet()
        log_id = base_log.create_base_log(request, title, operationmodule, action)
        return Response(data={"info": "删除操作记录成功"}, status=status.HTTP_200_OK)


class MatterLog(viewsets.ModelViewSet):

    queryset = OperateLog.objects.all()

    # 创建问题记录
    def create_log(self, log_id, name, new_value):
        """
        创建问题记录
        :param request:
        :param pk:
        :return:
        """
        detail_dict = {
            "name": name,
            "new_value": new_value,
            "log_id": log_id
        }
        ret = DetailLog.objects.create(**detail_dict)
        return ret

    def apply_again(self, pk, data, log_id):
        """
        再次申请改动记录
        :param request:
        :param pk:
        :return:
        """
        matter_dict = Matter.objects.filter(pk=pk).\
            values('matter_type', 'matter_name', 'training_method',
                   'description_customer', 'online_module','unonline_module',
                   'training_contact','training_contactnum','training_contactqq',
                   'training_position')
        matter_words = matter_word(Matter)
        data["matter_type"] = "培训"
        for da in data:
            new_values = data[da]
            # 获取新值和旧值
            if da == "training_method":
                old_values = dict(TRAINING_METTART_METHOD)[matter_dict[0].get(da)]
                if old_values != new_values:
                    detail_dict = {
                        "word": da,
                        #       字段中文名称
                        "name": matter_words[da],
                        "old_value": old_values,
                        "new_value": new_values,
                        "log_id": log_id
                    }
                    DetailLog.objects.create(**detail_dict)
            elif da in matter_dict[0]:
                old_values = matter_dict[0].get(da)
                if str(old_values) != str(new_values):
                    detail_dict = {
                        "word": da,
                        #       字段中文名称
                        "name": matter_words[da],
                        "old_value": old_values,
                        "new_value": new_values,
                        "log_id": log_id
                    }
                    DetailLog.objects.create(**detail_dict)
            else:
                pass
        return 'ok'

    def train_contact(self, pk, data, log_id):
        """
        联系人变更记录
        :param pk:
        :param data:
        :param log_id:
        :param contact_info:
        :return:
        """
        detail_list = []
        matter_words = matter_word(Matter)
        matter_dict = Matter.objects.filter(pk=pk).values("training_contact", "training_contactnum", "training_contactqq", "training_position").first()

        for contact in matter_dict:
            old_value = matter_dict.get(contact)
            new_value = data[contact]
            #   新值               旧值
            if new_value != old_value:
                detail_dict = {
                    "word": contact,
                    "name": matter_words[contact],
                    "old_value": old_value,
                    "new_value": new_value,
                    "log_id": log_id
                }
                detail_list.append(DetailLog(**detail_dict))
        ret = DetailLog.objects.bulk_create(detail_list)
        return ret

    def status_change(self, pk, log_id, new_status):
        """
        问题状态变更改动记录
        :param pk:
        :param log_id:
        :param new_status:
        :return:
        """
        matter = Matter.objects.get(pk=pk)
        if matter.matter_status != new_status:
            detail_dict = {
                "word": "matter_status",
                "name": "问题状态",
                "new_value": dict(MATTER_STATUS)[new_status],
                "old_value": dict(MATTER_STATUS)[matter.matter_status],
                "log_id": log_id
            }
            DetailLog.objects.create(**detail_dict)
        else:
            pass
        return 'ok'

    def teacher_change(self, pk, log_id, new_teacher):
        """
        培训讲师变更记录
        :param pk:
        :param log_id:
        :return:
        """
        # 老师的userid
        matter = Matter.objects.get(pk=pk).training_instructors
        if matter is not None:
            old_value = matter.last_name
        else:
            old_value = None
        #  新值            #旧值
        if new_teacher != old_value:
            detail_dict = {
                "word": "training_instructors",
                "name": "培训讲师",
                "old_value": old_value,
                "new_value": new_teacher,
                "log_id": log_id
            }
            DetailLog.objects.create(**detail_dict)
        else:
            pass
        return 'ok'

    def date_change(self, pk, log_id, new_start, new_end):
        """
        开始时间/结束时间变更记录
        :param pk:
        :param log_id:
        :param new_start:
        :param new_end:
        :return:
        """
        try:
            aa = str_to_date(new_start)
        except:
            pass
        matter = Matter.objects.get(pk=pk)

        old_start = matter.start_time
        if old_start is not None:
            old_start = date_to_str(old_start, format='%Y-%m-%d %H:%M:%S')
        if old_start != new_start:
            dict1 = {
                "word": "start_time",
                "name": "开始时间",
                "old_value": old_start,
                "new_value": new_start,
                "log_id": log_id
            }
            DetailLog.objects.create(**dict1)

        old_end = matter.end_time
        if old_end is not None:
            old_end = date_to_str(old_end, format='%Y-%m-%d %H:%M:%S')
        # 如果结束时间不为空
        if old_end != new_end:
            dict2 = {
                "word": "end_time",
                "name": "结束时间",
                "old_value": old_end,
                "new_value": new_end,
                "log_id": log_id
            }
            DetailLog.objects.create(**dict2)
        return 'ok'

    def matter_describe(self, pk, log_id, new_description):
        """
        问题描述变更
        :param pk:
        :param log_id:
        :param new_description:
        :return:
        """
        matter = Matter.objects.get(pk=pk)
        old_value = matter.problem_description
        if new_description != old_value:
            descrip_dict = {
                "word":"problem_description",
                "name": "问题描述",
                "old_value": old_value,
                "new_value": new_description,
                "log_id": log_id
            }
            DetailLog.objects.create(**descrip_dict)
        return 'ok'

    def reject_change(self, pk, dismiss_reason, log_id):
        """
        驳回理由变更记录
        :param pk:
        :param dismiss_reason:
        :param log_id:
        :return:
        """
        ject_count = Reject.objects.filter(correlation_id=pk, reject_type=1).count()
        # 第一次驳回不记录变更
        if ject_count > 0:
            old_value = Reject.objects.filter(correlation_id=pk, reject_type=1).order_by('-id').first().dismiss_reason
            new_value = dismiss_reason

            if old_value != new_value:
                detail_dict = {
                    "word": "dismiss_reason",
                    "name": "驳回理由",
                    "old_value": old_value,
                    "new_value": new_value,
                    "log_id": log_id
                }
                DetailLog.objects.create(**detail_dict)
        else:
            pass


class ProConfigLog:

    def status_change(self, pk, log_id, new_status):
        """
        产品配置状态记录
        :param pk:
        :param log_id:
        :param new_status:
        :return:
        """
        product_config = ProductConfig.objects.get(pk=pk)
        if product_config.product_stautus != new_status:
            detail_dict = {
                "word": "product_stautus",
                "name": "产品配置状态",
                "new_value": dict(PRODUCT_STATUS)[new_status],
                "old_value": dict(PRODUCT_STATUS)[product_config.product_stautus],
                "log_id": log_id
            }
            DetailLog.objects.create(**detail_dict)
        else:
            pass
        return 'ok'

    def porconfig_apply(self, pk, data, log_id):
        """
        产品配置修改
        :param pk:
        :param data: 修改后的数据
        :param log_id:
        :return:
        """
        # 旧数据
        config_dict = ProductConfig.objects.filter(pk=pk).\
            values('children_station', 'workorder_theme', 'subordinatemodule',
                   'func_name', 'func_value', 'describe', )[0]
        # 产品字段中英文
        pro_words = matter_word(ProductConfig)

        # 新数据
        for key, values in data.items():
            # 新数据       #旧数据
            if values != config_dict[key]:
                detail_dict = {
                    "word": key,
                    "name": pro_words[key],
                    "new_value": values,
                    "old_value": config_dict[key],
                    "log_id": log_id
                }
                DetailLog.objects.create(**detail_dict)
            else:
                pass
        return 'ok'


class VersionLog:

    @classmethod
    def change_status(self, request, schedule, step, product_name, version_id):
        """
        版本管理-改动记录
        :param request:
        :param schedule: 版本进度信息
        :param step: 当前操作的进度
        :param product_name: 产品名称
        :param version_id: 版本id
        :return:
        """
        old_value = schedule[-1]["button_log"]["old"]
        new_value = schedule[-1]["button_log"]["new"]
        if old_value != new_value:
            log_id = OpenStationViewSet.create_base_log(request, version_id, "版本流程", 3)
            detail = {
                "word": step,
                "name": product_name,
                "old_value": old_value,
                "new_value": new_value,
                "log_id": log_id
            }
            DetailLog.objects.create(**detail)
        else:
            pass
        return product_name


# LOG操作模块字段变更
def change_word():
    """
    LOG操作模块字段变更
    :return:
    """
    log_str = log_str_change
    for k, v in log_str.items():
        ret = OperateLog.objects.all().filter(operationmodule=k).update(operationmodule=v)
    return 'ok'