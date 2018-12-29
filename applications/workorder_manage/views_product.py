import datetime
from django.db import transaction

from django.contrib.auth.models import User, Group
from libs.datetimes import str_to_date, datetime_delta, date_to_str
from libs.excel_base import Excel_export
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route, permission_classes

from applications.production_manage.models import FunctionInfo, Grid
from applications.workorder_manage.views_matter import MatterFlowViewsets, SimpleMatterViewsets
from applications.workorder_manage.models import ProductConfig, StationInfo, OpenStationManage, \
    Attachment, Reject
from applications.workorder_manage.views import CommonOpenSet
from ldap_server.configs import PRODUCT_STATUS, Subordinate_Module, DEPLOY_WAYS
from applications.log_manage.views import ProConfigLog, OpenStationViewSet,MatterLog


class SimpleProductConfigurationSet(viewsets.ModelViewSet):

    queryset = ProductConfig.objects.all()

    @detail_route(methods=['GET'])
    def get_func(self, request, pk=None, *args, **kwargs):
        """
        获取站点的所有功能开关
        :param khkid:
        :return:
        """
        func_result = FunctionInfo.objects.filter(func_type="单选框", selection__station__company_info__id=pk).\
            select_related('id', 'func_name', 'selection__select_name').values('id', 'func_name','selection__select_name')
        return Response({"func_list": func_result})

    @detail_route(methods=['GET'])
    def get_select_name(self, request, pk=None, *args, **kwargs):
        """
        该功能开关的所有选项值
        :param id:
        :return:
        """
        name_list = FunctionInfo.objects.filter(pk=pk).select_related('selection__select_name').values('selection__select_name')
        return Response(name_list, status=status.HTTP_200_OK)

    @detail_route(methods=['GET'])
    def get_station_info(self, request, pk=None, *args, **kwargs):
        """
        返回公司站点信息
        :return:
        """
        matter_station = MatterFlowViewsets()
        station_company = matter_station.get_comstaion(pk)
        return Response(station_company, status=status.HTTP_200_OK)

    @detail_route(methods=['GET'])
    def get_children(self, request, pk=None, *args, **kwargs):
        """
        获取一个公司的所有子站
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        print('pk==', pk)
        open_exits = OpenStationManage.objects.filter(company_info=pk).exists()
        if open_exits:
            open_id = OpenStationManage.objects.get(company_info=pk)
            company_id = StationInfo.objects.filter(open_station__its_parent=open_id).values('company_id')
        else:
            company_id = ""
        return Response(company_id)

    @list_route(methods=['GET'])
    def get_module(self, request, *args, **kwargs):
        """
        获取产品配置的所属模块
        :param request:
        :return:
        """
        modeul = dict(Subordinate_Module)
        return Response(modeul, status=status.HTTP_200_OK)

    @classmethod
    def product_button(self, pk):
        """
        产品配置按钮展示
        :param pk:
        :return:
        """
        product_stautus = ProductConfig.objects.get(pk=pk).product_stautus
        button_list = []
        if product_stautus == 3:
            button_list = ['分配处理人', '驳回']
        elif product_stautus == 4:
            button_list = ['云平台操作完成']
        elif product_stautus == 5 or product_stautus == 7:
            button_list = ['操作方验证']
        elif product_stautus == 6:
            button_list = ['运维操作完成']
        elif product_stautus == 8:
            button_list = ['操作方验证通过', '操作方验证不通过']
        elif product_stautus == 9:
            button_list = ['需求方验证通过', '需求方验证不通过']
        elif product_stautus == 10:
            button_list = ['任务关闭']
        elif product_stautus == 12:
            button_list = ["再次申请"]
        return button_list

    @detail_route(methods=['GET'])
    def tell_khkid(self, request, pk=None, *args, **kwargs):
        """
        根据产品配置id获取客户库的id
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        khk_id = ProductConfig.objects.get(pk=pk).khk_id
        return Response({"khk_id": khk_id}, status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def create_mark(self, request):
        """
        产品配置备注新增按钮
        :param request:
        :return:
        """
        matter = SimpleMatterViewsets()
        data = request.data
        content = data.get("content")
        correlation_id = data.get("correlation_id")
        matter.create_remark(request, content, 4, correlation_id)
        return Response({"info": "创建成功"}, status=status.HTTP_200_OK)

    @detail_route(methods=['GET'])
    def get_remark(self, request, pk=None, *args, **kwargs):
        """
        备注和改动记录
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        mark_list = SimpleMatterViewsets.get_martkdef(4, pk)
        log_list = SimpleMatterViewsets.get_change_record('产品配置管理', 3, pk)
        return Response({"mark": mark_list, "log": log_list}, status=status.HTTP_200_OK)


class ProductConfigurationSet(viewsets.ModelViewSet):
    queryset = ProductConfig.objects.all()

    def create(self, request, *args, **kwargs):
        """
        产品配置创建
        :param request:
        :return:
        """
        data = request.data
        # 子站点
        children_station = data.get("children_station")
        # 客户库id
        khk_id = data.get("khk_id")
        # 工单主题
        workorder_theme = data.get("workorder_theme")
        # 所属模块
        subordinatemodule = data.get("subordinatemodule")
        # 功能名称
        func_name = data.get("func_name")
        # 功能选项值
        func_value = data.get("func_value")
        # 描述
        describe = data.get("describe")
        # 附件
        enclosure = data.get("enclosure")

        # 获取开站id
        open_id = OpenStationManage.objects.get(company_info=khk_id).id

        product_dict = {
            "children_station": children_station,
            "open_id": open_id,
            "workorder_theme": workorder_theme,
            "subordinatemodule": subordinatemodule,
            "func_name": func_name,
            "func_value": func_value,
            "describe": describe,
            "product_stautus": 3,
            "khk_id": khk_id
        }

        ret = ProductConfig.objects.create(**product_dict)
        # 改动记录
        log_id = OpenStationViewSet.create_base_log(request, ret.id, "产品配置管理", 3)
        ma_log = MatterLog()
        ma_log.create_log(log_id, '创建产品配置', '创建产品配置')
        if enclosure != [] or enclosure != '[]':
            SimpleMatterViewsets.create_attachment(enclosure, "新增产品配置", 2, ret.id)
        return Response({"info": "产品配置创建成功"}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        产品配置列表
        :param request:
        :return:
        """
        matter = MatterFlowViewsets()
        khk_id = request.GET.get('khk_id')
        page = request.GET.get('page', 1)
        page = int(page)

        data_list = []

        # 获取产品配置相关的信息
        base_query = ProductConfig.objects.\
            values('id', 'workorder_theme', 'subordinatemodule', 'func_name', 'func_value', 'product_stautus',
                   'created_at', 'open_id').order_by('-id')
        if khk_id:
            base_query = ProductConfig.objects.filter(khk_id=khk_id). \
                values('id', 'workorder_theme', 'subordinatemodule', 'func_name', 'func_value', 'product_stautus',
                       'created_at', 'open_id').order_by('-id')

        total_count = base_query.count()
        total_page, total_count, start, end = matter.page_set(total_count, page)

        for query in base_query[start:end]:
            open_id = query["open_id"]
            station_info = StationInfo.objects.filter(open_station=open_id)
            if len(station_info) > 0:
                station_info = station_info.values('deploy_way', 'grid')[0]
                station_info["deploy_way"] = dict(DEPLOY_WAYS).get(station_info["deploy_way"])
                station_info["grid"] = Grid.objects.get(pk=station_info["grid"]).grid_name
            else:
                station_info = dict()
                station_info["deploy_way"] = "无"
                station_info["grid"] = "无"
            query["product_stautus"] = dict(PRODUCT_STATUS).get(query["product_stautus"])
            query.update(station_info)
            query["created_at"] = date_to_str(query["created_at"], format='%Y-%m-%d %H:%M:%S')

            data_list.append(query)

        page_dict = {"total_count": total_count, "total_page": total_page}
        return Response(data={"page_num": page_dict, "result": data_list}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    def problem_solver(self, request, pk=None, *args, **kwargs):
        """
        分配处理人
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        log_id = OpenStationViewSet.create_base_log(request, pk, '产品配置管理', 3)
        product_log = ProConfigLog()

        data = request.data
        # 处理人id
        dealing_person = data.get("dealing_person")
        task_type = self.get_task_type(dealing_person)
        # 备注
        content = data.get("content")
        # 分配人
        allocation_people = request.user

        # 处理人
        dealing_person = User.objects.get(pk=dealing_person)
        product_config = ProductConfig.objects.get(pk=pk)
        try:
            with transaction.atomic():
                product_config.dealing_person = dealing_person
                product_config.allocation_people = allocation_people.last_name
                product_config.allocate_time = datetime.datetime.now()

                # 平台组
                if task_type == 1:
                    # 记录产品配置状态变更
                    product_log.status_change(pk, log_id, 4)
                    product_config.product_stautus = 4

                else:
                    # 记录产品配置状态变更
                    product_log.status_change(pk, log_id, 6)
                    product_config.product_stautus = 6
                product_config.save()
                # 备注
                matter = SimpleMatterViewsets()
                # 新增备注
                matter.create_remark(request, content, 4, pk)
        except Exception as e:
            raise TypeError(e)
        return Response({"info": "分配完成"}, status=status.HTTP_200_OK)

    def get_task_type(self, user_id):
        """
        通过用户的分组判断任务类型
        :param pk: 产品配置id
        :return:
        """
        user_id = int(user_id)
        platform = Group.objects.get(name="平台组").user_set.values('id')
        operations = Group.objects.get(name="运维").user_set.values('id')

        if {'id': user_id} in platform:
            # 平台组
            task_type = 1
        elif {'id': user_id} in operations:
            # 运维操作
            task_type = 2
        else:
            task_type = 0
        return task_type

    @detail_route(['PUT'])
    def product_open(self, request, pk=None, *args, **kwargs):
        """
        开站2，3步
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        common_open = CommonOpenSet()
        # 产品配置记录
        product_log = ProConfigLog()

        # 开站id
        open_id = data.get("open_id")

        children_id = data.get("children_id")

        sta_data = data.get("station_info")
        func_list = data.get("func_list")

        # 获取  要修改的站点的open_id
        #要得目的  如果childre_id 不为None，要修改的是子站，对open_id = children_id
        # childre_id 为 None  表达式为True  执行
        # 1. childeren =None 2. children_di=34534

        if children_id != None:
            # 修改子站
            parents = 1
            open_id = int(children_id)
        elif children_id == None:
            open_id = int(open_id)
            parents = 0

        open = OpenStationManage.objects.get(pk=open_id)


        station_info = open.station_info
        company_id = station_info.company_id
        online_status = open.online_status
        input_pact_products = sta_data["pact_products"]

        """
        开站管理2、3步
        """
        try:
            with transaction.atomic():
                log_id = OpenStationViewSet.create_base_log(request, pk, '产品配置管理', 3)

                # 更新站点信息
                common_open.open_update_station(open, station_info, sta_data, parents)
                # 更新站点的功能开关信息
                common_open.open_funclist(open, func_list)
                # 判断该open_id的站点是经典版1还是重构版2
                classify = common_open.get_classify(open_id)
                if classify == 1 and parents == 0:
                    common_open.open_servergrouup(station_info, sta_data, classify)
                # 如果站点状态是开站
                if online_status is True:
                    # 开站
                    common_open.open_manage(company_id, online_status, classify)
                # 获取修改前的站点到期时间和产品名称列表
                pre_station_info = StationInfo.objects.filter(open_station__id=open_id).select_related(
                    'pact_products__product').values_list('pact_products__product', 'close_station_time')
                common_open.new_product(company_id,pre_station_info, input_pact_products)
                common_open.open_renewal(pre_station_info, company_id, sta_data)
                """
                产品配置
                """
                product_config = ProductConfig.objects.get(pk=pk)
                current_state = product_config.product_stautus
                # 实际开始时间
                actual_start_time = data.get("actual_start_time")
                # 实际完成时间
                actual_completion_time = datetime.datetime.now()
                product_config.actual_start_time = actual_start_time
                product_config.actual_completion_time = actual_completion_time
                if current_state == 4:
                    # 记录产品配置状态变更
                    product_log.status_change(pk, log_id, 5)
                    product_config.product_stautus = 5
                elif current_state == 6:
                    # 记录产品配置状态变更
                    product_log.status_change(pk, log_id, 7)
                    product_config.product_stautus = 7
                product_config.save()
        except Exception as e:
            raise TypeError(e)
        return Response({"info": "操作完成"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    def put_proconfig(self, request, pk=None, *args, **kwargs):
        """
        再次申请
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        # 子站点
        children_station = data.get("children_station")
        # 工单主题
        workorder_theme = data.get("workorder_theme")
        # 所属模块
        subordinatemodule = data.get("subordinatemodule")
        # 功能名称
        func_name = data.get("func_name")
        # 功能选项值
        func_value = data.get("func_value")
        # 描述
        describe = data.get("describe")
        # 附件
        enclosure = data.get("enclosure")

        product_config = ProductConfig.objects.get(pk=pk)
        # 产品配置记录
        product_log = ProConfigLog()
        try:
            with transaction.atomic():
                log_id = OpenStationViewSet.create_base_log(request, pk, '产品配置管理', 3)
                product_config.children_station = children_station
                product_config.workorder_theme = workorder_theme
                product_config.subordinatemodule = subordinatemodule
                product_config.func_name = func_name
                product_config.func_value = func_value
                product_config.describe = describe
                # 记录产品配置状态变更
                product_log.status_change(pk, log_id, 3)
                product_config.product_stautus = 3
                product_config.save()
                if enclosure != [] or enclosure != '[]':
                    # 删除该产品配置的原有附件
                    ret = Attachment.objects.filter(atta_type=2, correlation_id=pk).delete()
                    # 新增附件
                    SimpleMatterViewsets.create_attachment(enclosure, "重新申请", 2, pk)
        except Exception as e:
            raise TypeError(e)
        return Response({"info": "产品配置修改成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    def reject(self, request, pk=None, *args, **kwargs):
        data = request.data
        # 驳回原因
        dismiss_reason = data.get("dismiss_reason")
        # 附件
        enclosure = data.get("enclosure")
        # 产品配置记录
        product_log = ProConfigLog()

        try:
            with transaction.atomic():
                # 驳回操作
                ret = Reject.objects.create(dismiss_reason=dismiss_reason, correlation_id=pk, reject_type=2)
                log_id = OpenStationViewSet.create_base_log(request, pk, '产品配置管理', 3)
                # 新增附件
                if enclosure != [] or enclosure != '[]':
                    SimpleMatterViewsets.create_attachment(enclosure, "产品配置驳回", 2, pk)
                # 记录产品配置状态变更
                product_log.status_change(pk, log_id, 12)
                status_ret = ProductConfig.objects.filter(pk=pk).update(product_stautus=12)
        except Exception as e:
            raise TypeError(e)
        return Response({"info": "驳回成功"}, status=status.HTTP_200_OK)

    @detail_route(['GET'])
    def operator_verification(self, request, pk=None, *args, **kwargs):
        """
        操作方验证
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        # 产品配置记录
        product_log = ProConfigLog()
        try:
            with transaction.atomic():
                log_id = OpenStationViewSet.create_base_log(request, pk, '产品配置管理', 3)
                product_log.status_change(pk, log_id, 8)
                ret = ProductConfig.objects.filter(pk=pk).update(product_stautus=8)
        except Exception as e:
            raise TypeError(e)
        return Response(status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    def verification_pass(self, request, pk=None, *args, **kwargs):
        """
        验证通过，任务关闭，根据当前产品配置的状态执行对应的操作
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        # 备注
        content = data.get("content")
        # 附件
        enclosure = data.get("enclosure")
        # 产品配置记录
        product_log = ProConfigLog()
        product_config = ProductConfig.objects.get(pk=pk)
        try:
            with transaction.atomic():
                log_id = OpenStationViewSet.create_base_log(request, pk, '产品配置管理', 3)

                product_status = product_config.product_stautus
                # 操作方验证通过
                if product_status == 8:
                    product_log.status_change(pk, log_id, 9)
                    product_config.product_stautus = 9
                    if enclosure != [] or enclosure != '[]':
                        SimpleMatterViewsets.create_attachment(enclosure, "操作方验证通过", 2, pk)
                # 需求方验证通过
                elif product_status == 9:
                    product_log.status_change(pk, log_id, 10)
                    product_config.product_stautus = 10
                    # 新增附件
                    if enclosure != [] or enclosure != '[]':
                        SimpleMatterViewsets.create_attachment(enclosure, "需求方验证通过", 2, pk)
                # 任务关闭
                elif product_status == 10:
                    product_log.status_change(pk, log_id, 11)
                    product_config.product_stautus = 11
                    # 新增附件
                    if enclosure != [] or enclosure != '[]':
                        SimpleMatterViewsets.create_attachment(enclosure, "任务关闭", 2, pk)
                product_config.save()

                # 新增备注
                matter = SimpleMatterViewsets()
                matter.create_remark(request, content, 4, pk)
        except Exception as e:
            raise TypeError(e)
        return Response(status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    def fail_verification(self, request, pk=None, *args, **kwargs):
        """
        验证不通过
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        # 不通过原因
        dismiss_reason = data.get("dismiss_reason")
        # 附件
        enclosure = data.get("enclosure")

        product_status = ProductConfig.objects.get(pk=pk).product_stautus
        # 产品配置记录
        product_log = ProConfigLog()
        # try:
        #     with transaction.atomic():
        log_id = OpenStationViewSet.create_base_log(request, pk, '产品配置管理', 3)
        # 操作方验证通过
        if product_status == 8:
            ret = Reject.objects.create(dismiss_reason=dismiss_reason, correlation_id=pk, reject_type=3)
            if enclosure != [] or enclosure != '[]':
                # 新增附件
                SimpleMatterViewsets.create_attachment(enclosure, "操作方验证不通过", 2, pk)
        # 需求方验证通过
        elif product_status == 9:
            ret = Reject.objects.create(dismiss_reason=dismiss_reason, correlation_id=pk, reject_type=4)
            if enclosure != [] or enclosure != '[]':
                # 新增附件
                SimpleMatterViewsets.create_attachment(enclosure, "需求方验证不通过", 2, pk)
        product_log.status_change(pk, log_id, 3)
        # 验证不通过
        ret = ProductConfig.objects.filter(pk=pk).update(product_stautus=3)
        # except Exception as e:
        #     raise TypeError(e)
        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        详情接口
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # instance = self.get_object()
        # serializer = self.get_serializer(instance)
        pk = kwargs["pk"]
        config_tuple = ('id', 'children_station','workorder_theme', 'subordinatemodule', 'func_name', 'func_value', 'allocation_people', 'dealing_person',
                        'product_stautus', 'khk_id', 'allocate_time', 'actual_start_time', 'actual_completion_time', 'created_at', 'updated_at',
                        'open_id', 'describe')
        # 获取产品配置基础详情信息
        config_dict = ProductConfig.objects.filter(pk=pk).values(*config_tuple)[0]
        # 获取该客户库的公司站点信息
        matter = MatterFlowViewsets()
        # 公司id
        khk_id = config_dict["khk_id"]
        company_station = matter.get_comstaion(khk_id)
        # 将公司站点信息添加到产品配置的详情中
        config_dict.update(company_station)
        # 附件
        atta_exits = Attachment.objects.filter(atta_type=2, correlation_id=kwargs["pk"]).exists()
        atta_list = None
        if atta_exits:
            atta_list = Attachment.objects.filter(atta_type=2, correlation_id=kwargs["pk"]).values('id', 'enclosure')
        config_dict["matter_ofatta"] = atta_list
        """
        字段信息整理
        """
        # 处理人
        if config_dict["dealing_person"] != None:
            config_dict["dealing_person"] = User.objects.get(pk=config_dict["dealing_person"]).last_name
        # 产品配置
        config_dict["product_stautus"] = dict(PRODUCT_STATUS)[config_dict["product_stautus"]]
        """
        时间格式化
        """
        # 创建时间
        config_dict["created_at"] = date_to_str(config_dict["created_at"], format='%Y-%m-%d %H:%M:%S')
        # 更新时间
        config_dict["updated_at"] = date_to_str(config_dict["updated_at"], format='%Y-%m-%d %H:%M:%S')
        # 分配时间
        if config_dict["allocate_time"] != None:
            config_dict["allocate_time"] = date_to_str(config_dict["allocate_time"], format='%Y-%m-%d %H:%M:%S')
        # 实际开始时间
        if config_dict["actual_start_time"] != None:
            config_dict["actual_start_time"] = date_to_str(config_dict["actual_start_time"], format='%Y-%m-%d %H:%M:%S')
        # 实际完成时间
        if config_dict["actual_completion_time"] != None:
            config_dict["actual_completion_time"] = date_to_str(config_dict["actual_completion_time"], format='%Y-%m-%d %H:%M:%S')
        """
        增加数据库没有的数据
        """
        children_station = config_dict.get("children_station")

        children_id = None
        # 子站存在
        if children_station != '':
            children_id = OpenStationManage.objects.filter(open_station__company_id=children_station).first().id
        # 如果有its_parent 该站点为子站，否则为父站
        config_dict["children_id"] = children_id
        config_dict["matter_type"] = "产品配置"
        """
        产品配置按钮
        """
        button_list = SimpleProductConfigurationSet.product_button(pk)
        config_dict["button_list"] = button_list
        """
        驳回次数
        """
        reject_count = Reject.objects.filter(correlation_id=pk, reject_type=2).count()
        config_dict["reject_count"] = reject_count
        # 需求方不通过原因次数
        config_dict["demand_count"] = Reject.objects.filter(correlation_id=pk, reject_type=4).count()
        # 操作方不通过原因次数
        config_dict["operation_count"] = Reject.objects.filter(correlation_id=pk, reject_type=3).count()
        return Response(config_dict, status=status.HTTP_200_OK)