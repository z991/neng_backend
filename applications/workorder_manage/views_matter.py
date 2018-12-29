from django.contrib.auth.models import User, Group
from libs.datetimes import str_to_date, datetime_delta, date_to_str
from libs.excel_base import Excel_export
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import operator

from applications.workorder_manage.serializers import MatterSerializer
from applications.workorder_manage.models import Matter, StationInfo, Reject,CompanyInfo, ContactInfo, \
    Attachment, RemarkEvolve, ProductConfig
from ldap_server.configs import TRAINING_METTART_METHOD, WAY_MATTERCOMMUNICATE, SATISFACTION_SURVEY, MATTER_TYPE, \
    MATTER_STATUS, DEPLOY_WAYS, Y_NLEGACY, CLI_CHOICES
from applications.log_manage.models import OperateLog, DetailLog
from applications.log_manage.views import OpenStationViewSet, MatterLog
from applications.setup.permissions import CreateTrainPermission, LecturerPermission, CommunicationPermission, PersonnelAllocationPermission, HandoverIssuesPermission, \
    RejectPermission, DetermineSchedulingPermission, IdentificationIssuesPermission, TerminationTrainingPermission,\
    TrainingPreparePermission, SetPendingPermission, TrainningPermission,SatisfactionSurveyPermission, RemarkPermission
from applications.production_manage.models import Grid


# 解决csrf
class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    参考http://stackoverflow.com/questions/30871033/django-rest-framework-remove-csrf
    """
    def enforce_csrf(self, request):
        return


class MatterFlowViewsets(viewsets.ModelViewSet):
    queryset = Matter.objects.all().order_by('-id')
    serializer_class = MatterSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_comstaion(self, company_pk):
        """
        获取公司&站点表的信息
        :param company_pk:
        :return:
        """
        company_info = CompanyInfo.objects.get(pk=company_pk)
        station_info_exit = StationInfo.objects.filter(open_station__company_info__id=company_pk).exists()
        if station_info_exit is True:
            station_info = StationInfo.objects.get(open_station__company_info__id=company_pk)
            # 企业id
            company_id = station_info.company_id
            # 运营支持
            oper_supt = station_info.oper_supt
            # 实施顾问
            impl_cslt = station_info.impl_cslt
            # 节点
            grid = Grid.objects.get(pk=station_info.grid.id).grid_name
        else:
            company_id = None
            oper_supt = None
            impl_cslt = None
            grid = None

        # 部署方式
        deploy_way = dict(DEPLOY_WAYS).get(company_info.deploy_way)
        # 公司名称
        company_name = company_info.company_name
        # 商务
        try:
            linkman = ContactInfo.objects.filter(company=company_pk).filter(link_type=1).first().linkman
        except:
            linkman = None
        # 客户版本
        cli_version = company_info.cli_version
        if cli_version != None:
            cli_version = dict(CLI_CHOICES).get(cli_version)

        dic_comstaion = {"company_name": company_name, "deploy_way": deploy_way, "company_id": company_id,
                         "oper_supt": oper_supt, "impl_cslt": impl_cslt,"grid": grid,  "commercial": linkman,
                         "cli_version": cli_version}
        return dic_comstaion

    def page_set(self, total_count, page):
        """
        分页，每页10条数据
        :param total_count:
        :param page:
        :return:
        """
        page_list = []
        if total_count < 10:
            total_page = 1
            page_list.append(total_page)
        # 如果总条数是十的整数倍
        elif total_count % 10 == 0 and total_count >= 10:
            total_page = total_count // 10
            page_list.append(total_page)
            # 如果总条数不是十的整数倍
        elif total_count % 10 != 10 and total_count >= 10:
            total_page = total_count // 10 + 1
            page_list.append(total_page)
        # 第一页
        if page == 1:
            start = 0
            end = 10
        else:
            start = (page-1) * 10
            end = page * 10
        return page_list[0], total_count, start, end

    def get_trainfo(self, pk):
        """
        获取培训相关信息
        :param pk:
        :return:
        """
        matter = Matter.objects.get(pk=pk)

        instructors_id = matter.training_instructors
        if instructors_id == None:
            training_instructors = None
        else:
            training_instructors = instructors_id.last_name
        train_method = dict(TRAINING_METTART_METHOD).get(matter.training_method)

        start_time = matter.start_time
        if start_time is not None:
            start_time = date_to_str(start_time, format='%Y-%m-%d %H:%M:%S')
        end_time = matter.end_time
        if end_time is not None:
            end_time = date_to_str(end_time, format='%Y-%m-%d %H:%M:%S')
        training_contact = matter.training_contact
        training_model = matter.training_model
        if training_model != None:
            training_model = eval(training_model)

        data_dict = {"training_instructors": training_instructors, "training_method": train_method,
                     "training_contact": training_contact, "start_time": start_time,
                     "end_time": end_time, "training_model": training_model}
        return data_dict

    @list_route(['GET'])
    def khkl_train(self, request):
        """
        培训列表
        :param request:
        :return:
        """
        # 获取企业id
        company_pk = request.GET.get("company_pk")
        page = request.GET.get("page", 1)
        page = int(page)

        base_query = Matter.objects.all().filter(company_matter=company_pk)
        total_count = base_query.count()

        total_page, total_count, start, end = self.page_set(total_count, page)
        # 获取公司&站点信息
        dic_comstaion = self.get_comstaion(company_pk)

        queryset = base_query.values('id').order_by('-updated_at')[start:end]
        data_list = []
        index = start+1
        for q in queryset:
            id = q["id"]
            train_dict = self.get_trainfo(id)
            q.update(dic_comstaion)
            q.update(train_dict)
            q.update({"index": index})
            index += 1
            data_list.append(q)
        page_dict = {"total_count": total_count, "total_page": total_page}
        return Response(data={"page_num": page_dict, "result": data_list}, status=status.HTTP_200_OK)

    @list_route(['GET'])
    def train_list(self, request):
        """
        培训管理-培训列表
        :param request:
        :return:
        """
        page = request.GET.get("page", 1)
        page = int(page)
        base_query = Matter.objects.all()
        total_count = base_query.count()

        # 获取分页
        total_page, total_count, start, end = self.page_set(total_count, page)

        querset = base_query.values('id', 'matter_status', 'company_matter').\
            order_by('-id')[start:end]
        data_list = []
        # 编号
        index = start + 1
        for q in querset:
            id = q["id"]
            company_matter = q["company_matter"]
            # 获取公司&站点信息
            dic_comstaion = self.get_comstaion(company_matter)
            train_dict = self.get_trainfo(id)
            q.update(dic_comstaion)
            q.update(train_dict)
            q["matter_status"] = dict(MATTER_STATUS).get(q["matter_status"])
            q.update({"index": index})
            data_list.append(q)
            index += 1
        page_dict = {"total_count": total_count, "total_page": total_page}
        return Response(data={"page_num": page_dict, "result": data_list}, status=status.HTTP_200_OK)

    def get_user(self, name):
        """
        根据用户名获取该用户实例
        :param name:
        :return:
        """
        user_verify = User.objects.filter(last_name=name).first()
        return user_verify

    def verify_teacher(self, request, pk):
        """
        校验当前问题的培训讲师是否为登录用户
        :param request:
        :param pk:
        :return:
        """
        matter_teacher = Matter.objects.get(pk=pk).training_instructors
        if request.user != matter_teacher:
            verify = 0
        else:
            verify = 1
        return verify

    @list_route(['POST'])
    @permission_classes([CreateTrainPermission, ])
    def create_train(self, request):
        data = request.data
        # 企业id
        company_pk = data.get("company_pk")
        # 问题类型
        matter_type = data.get("matter_type")
        # 经办人
        # responsible = data.get("responsible")
        # 问题名称
        matter_name = data.get("matter_name")
        # 培训方式
        training_method = data.get("training_method")
        # 客户状态描述
        description_customer = data.get("description_customer")
        # 已上线模块
        online_module = data.get("online_module")
        # 未上线模块
        unonline_module = data.get("unonline_module")
        # 培训联系人
        training_contact = data.get("training_contact")
        # 培训联系人电话
        training_contactnum = data.get("training_contactnum")
        # 培训联系人QQ
        training_contactqq = data.get("training_contactqq")
        # 培训联系人职位
        training_position = data.get("training_position")

        # company_matter = CompanyInfo.objects.get(pk=company_pk)
        # 获取当前登录用户
        responsibler = request.user

        train_dict = {
            "matter_type": matter_type,
            "responsible": responsibler,
            "matter_name": matter_name,
            "training_method": training_method,
            "description_customer": description_customer,
            "online_module": online_module,
            "unonline_module": unonline_module,
            "training_contact": training_contact,
            "training_contactnum": training_contactnum,
            "training_contactqq": training_contactqq,
            "training_position": training_position,
            "matter_status": 1,
            "company_matter": company_pk
        }
        ret = Matter.objects.create(**train_dict)
        # 改动记录
        ret = str(ret)
        log_id = OpenStationViewSet.create_base_log(request, ret, "培训管理", 3)
        ma_log = MatterLog()
        ma_log.create_log(log_id,'创建问题', '创建问题')
        return Response(data={"info": "问题创建成功"}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        问题详情
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        simp = SimpleMatterViewsets()
        # 获取
        button_list = simp.notice_button(request, data)

        # 添加公司&站点信息
        company_pk = data["company_matter"]
        dic_comstaion = self.get_comstaion(company_pk)
        data.update(dic_comstaion)
        data.update({"button_list": button_list})
        # 文题状态
        data["matter_status"] = dict(MATTER_STATUS)[data["matter_status"]]
        # 问题类型
        data["matter_type"] = dict(MATTER_TYPE)[data["matter_type"]]
        # 培训方式
        data["training_method"] = dict(TRAINING_METTART_METHOD)[data["training_method"]]
        data["final_training_method"] = dict(TRAINING_METTART_METHOD).get(data["final_training_method"])
        # 满意度等级
        data["satisfaction_level"] = dict(SATISFACTION_SURVEY).get(data["satisfaction_level"])
        # 沟通方式
        communication_way = instance.communication_way
        if communication_way != None:
            data["communication_way"] = eval(communication_way)
        else:
            data["communication_way"] = []
        # 上线模块
        online_module = instance.online_module
        if online_module != None:
            data["online_module"] = eval(online_module)
        else:
            data["online_module"] = []
        # 培训模块
        training_model = instance.training_model
        if training_model != None:
            data["training_model"] = eval(training_model)
        else:
            data["training_model"] = []

        # 培训讲师
        training_instructors = instance.training_instructors
        if training_instructors != None:
            training_instructors = training_instructors.last_name
        data["training_instructors"] = training_instructors
        # 经办人
        responsible = instance.responsible.last_name
        data["responsible"] = responsible
        # 问题处理人
        dealing_person = instance.dealing_person
        if dealing_person != None:
            dealing_person = dealing_person.last_name
        data["dealing_person"] = dealing_person
        # 是否有遗留问题
        legacy_issue = instance.legacy_issue
        if legacy_issue != None:
            legacy_issue = dict(Y_NLEGACY).get(data["legacy_issue"])
        data["legacy_issue"] = legacy_issue

        # 调查人员
        investigador = instance.investigador
        if investigador != None:
            investigador = investigador.last_name
        data["investigador"] = investigador
        # 调查开始时间
        invest_start = instance.invest_start
        if invest_start != None:
            invest_start = date_to_str(invest_start, format='%Y-%m-%d %H:%M:%S')
        data["invest_start"] = invest_start
        # 调查结束时间
        invest_end = instance.invest_end
        if invest_end != None:
            invest_end = date_to_str(invest_end, format='%Y-%m-%d %H:%M:%S')
        data["invest_end"] = invest_end
        # 附件
        atta_exits = Attachment.objects.filter(atta_type=1, correlation_id=kwargs["pk"]).exists()
        atta_list = None
        if atta_exits:
            atta_list = Attachment.objects.filter(atta_type=1, correlation_id=kwargs["pk"]).values('id', 'enclosure')
        data.update({"matter_ofatta": atta_list})

        # 添加驳回原因
        dismiss_exits = Reject.objects.filter(correlation_id=kwargs["pk"], reject_type=1).exists()
        if dismiss_exits:
            dismiss_reason = Reject.objects.filter(correlation_id=kwargs["pk"], reject_type=1).order_by("updated_at").first().dismiss_reason
            dismiss_count = Reject.objects.filter(correlation_id=kwargs["pk"], reject_type=1).count()
        else:
            dismiss_reason = None
            dismiss_count = 0
        data.update({"dismiss_reason": dismiss_reason, "dismiss_count": dismiss_count})
        return Response(data)

    @detail_route(['PUT'])
    @permission_classes([LecturerPermission, ])
    def distribution_lecturer(self, request, pk=None, *args, **kwargs):
        """
        分配讲师
        :param request:
        :param pk:
        :return:
        """
        data = self.request.data

        instructors = data.get("training_instructors")
        enclosure = data.get("enclosure")

        training_instructors = self.get_user(instructors)
        # 变更记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        mat_log = MatterLog()
        # 记录老师变更
        mat_log.teacher_change(pk, log_id, instructors)
        # 记录状态变更
        mat_log.status_change(pk, log_id, 2)

        matter = Matter.objects.get(pk=pk)
        matter.training_instructors = training_instructors
        matter.matter_status = 2

        matter.save()
        if enclosure != []:
            SimpleMatterViewsets.create_attachment(enclosure,"分配讲师", 1, pk)
        return Response({"info": "讲师分配成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([RejectPermission, ])
    def reject(self, request, pk=None, *args, **kwargs):
        """
        驳回
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        data = self.request.data
        dismiss_reason = data.get("dismiss_reason")
        # 状态变更记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        matter_log = MatterLog()
        matter_log.status_change(pk, log_id, 3)
        matter_log.reject_change(pk, dismiss_reason, log_id)

        matter = Matter.objects.get(pk=pk)
        matter.matter_status = 3
        matter.save()
        reject = Reject.objects.create(dismiss_reason=dismiss_reason, correlation_id=pk, reject_type=1)

        return Response({"info": "驳回成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([CreateTrainPermission, ])
    def put_train(self, request, pk=None, *args, **kwargs):
        """
        问题修改成功
        :param request:
        :param pk:
        :return:
        """
        matter_responsible = Matter.objects.get(pk=pk).responsible
        if request.user != matter_responsible and request.user.is_superuser is False:
            return Response({"error": "您不是该问题的经办人，无法操作"}, status=status.HTTP_400_BAD_REQUEST)
        data = self.request.data

        # 改动记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        ma_log = MatterLog()
        ma_log.apply_again(pk, data, log_id)
        ma_log.status_change(pk, log_id, 1)

        # 问题类型key-value 位置交换
        type_dict = dict(MATTER_TYPE)
        type_dict = {v: k for k, v in type_dict.items()}

        # 问题类型
        matter_type = data.get("matter_type")
        # 问题名称
        matter_name = data.get("matter_name")
        # 培训方式
        training_method = data.get("training_method")
        # 客户状态描述
        description_customer = data.get("description_customer")
        # 已上线模块
        online_module = data.get("online_module")
        # 未上线模块
        unonline_module = data.get("unonline_module")
        # 培训联系人
        training_contact = data.get("training_contact")
        # 培训联系人电话
        training_contactnum = data.get("training_contactnum")
        # 培训联系人QQ
        training_contactqq = data.get("training_contactqq")
        # 培训联系人职位
        training_position = data.get("training_position")
        # 培训方式key-value 位置交换
        method_dict = dict(TRAINING_METTART_METHOD)
        method_dict = {v: k for k, v in method_dict.items()}

        matter = Matter.objects.get(pk=pk)
        matter.matter_type = type_dict.get(matter_type)
        matter.matter_name = matter_name
        matter.training_method = method_dict.get(training_method)
        matter.description_customer = description_customer
        matter.online_module = online_module
        matter.unonline_module = unonline_module
        matter.training_contact = training_contact
        matter.training_contactnum = training_contactnum
        matter.training_contactqq = training_contactqq
        matter.training_position = training_position
        matter.matter_status = 1
        matter.save()

        return Response({"info": "信息修改成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([CommunicationPermission, ])
    def communication_requirements(self, request, pk=None, *args, **kwargs):
        """
        创建沟通需求
        :param request:
        :param pk:
        :return:
        """
        verify = self.verify_teacher(request, pk)
        if verify == 0 and request.user.is_superuser is False:
            return Response({"error": "该问题的培训老师不是您,无权操作！"}, status=status.HTTP_400_BAD_REQUEST)

        data = self.request.data
        instructors = data.get("training_instructors")
        # 培训联系人
        training_contact = data.get("training_contact")
        # 培训联系人电话
        training_contactnum = data.get("training_contactnum")
        # 培训联系人QQ
        training_contactqq = data.get("training_contactqq")
        # 培训联系人职位
        training_position = data.get("training_position")
        # 客户培训需求
        customer_training_needs = data.get("customer_training_needs")
        # 沟通方式
        communication_way = data.get("communication_way")
        # 最终培训方式
        final_training_method = data.get("final_training_method")
        # 培训预计开始时间
        start_time = data.get("start_time")
        # 培训预计结束时间
        end_time = data.get("end_time")
        # 未培训原因
        untrained_cause = data.get("untrained_cause")

        training_instructors = self.get_user(instructors)
        # 改动记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        mat_log = MatterLog()
        mat_log.train_contact(pk, data, log_id)
        mat_log.status_change(pk, log_id, 4)

        matter = Matter.objects.get(pk=pk)
        matter.training_instructors = training_instructors
        matter.training_contact = training_contact
        matter.training_contactnum = training_contactnum
        matter.training_contactqq = training_contactqq
        matter.training_position = training_position
        matter.customer_training_needs = customer_training_needs
        matter.communication_way = communication_way
        matter.final_training_method = final_training_method
        if start_time != '':
            matter.start_time = str_to_date(start_time)
        if end_time != '':
            matter.end_time = str_to_date(end_time)
        matter.untrained_cause = untrained_cause
        matter.matter_status = 4
        matter.save()

        return Response({"info": "沟通培训需求创建成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([TerminationTrainingPermission, ])
    def termination_training(self, request, pk=None, *args, **kwargs):
        """
        终止培训
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        data = self.request.data
        verify = self.verify_teacher(request, pk)
        if verify == 0 and request.user.is_superuser is False:
            return Response({"error": "该问题的培训老师不是您,无权操作！"}, status=status.HTTP_400_BAD_REQUEST)
        # 终止原因
        termination_reason = data.get("termination_reason")
        # 上传附件返回的数据
        enclosure = data.get("enclosure")
        # 改动记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        mat_log = MatterLog()
        mat_log.status_change(pk, log_id, 7)

        matter = Matter.objects.get(pk=pk)
        matter.termination_reason = termination_reason
        matter.matter_status = 7
        matter.save()
        if enclosure != []:
            SimpleMatterViewsets.create_attachment(enclosure, "客户终止培训", 1, pk)
        return Response({"info": "客户终止培训成功"}, status=status.HTTP_200_OK)

    @detail_route(['GET'])
    @permission_classes([SetPendingPermission, ])
    def set_pending(self, request, pk=None, *args, **kwargs):
        """
        状态挂起
        :param request:
        :param pk:
        :return:
        """
        verify = self.verify_teacher(request, pk)
        # 改动记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        mat_log = MatterLog()
        mat_log.status_change(pk, log_id, 6)
        if verify == 0 and request.user.is_superuser is False:
            return Response({"error": "该问题的培训老师不是您,无权操作！"}, status=status.HTTP_400_BAD_REQUEST)
        ret = Matter.objects.filter(pk=pk).update(matter_status=6)

        return Response({"info": "培训已挂起"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([TrainingPreparePermission, ])
    def training_prepare(self, request, pk=None, *args, **kwargs):
        """
        培训准备
        :param request:
        :param pk:
        :return:
        """
        verify = self.verify_teacher(request, pk)
        if verify == 0 and request.user.is_superuser is False:
            return Response({"error": "该问题的培训老师不是您,无权操作！"}, status=status.HTTP_400_BAD_REQUEST)
        data = self.request.data

        instructors = data.get("training_instructors")
        enclosure = data.get("enclosure")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        training_instructors = self.get_user(instructors)
        # 改动记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        matter_log = MatterLog()
        matter_log.status_change(pk, log_id, 5)
        matter_log.date_change(pk, log_id, start_time, end_time)

        matter = Matter.objects.get(pk=pk)
        matter.training_instructors = training_instructors
        matter.start_time = start_time
        matter.end_time = end_time
        matter.matter_status = 5
        matter.save()

        if enclosure != []:
            # 保存附件
            SimpleMatterViewsets.create_attachment(enclosure, "培训准备", 1, pk)

        return Response({"info": "培训准备完成"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([DetermineSchedulingPermission, ])
    def determine_scheduling(self, request, pk=None, *args, **kwargs):
        """
        确定排期
        :param request:
        :param pk:
        :return:
        """
        verify = self.verify_teacher(request, pk)
        if verify == 0 and request.user.is_superuser is False:
            return Response({"error": "该问题的培训老师不是您,无权操作！"}, status=status.HTTP_400_BAD_REQUEST)
        data = self.request.data

        start_time = data.get("start_time")
        end_time = data.get("end_time")
        # 改动记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        matter_log = MatterLog()
        matter_log.status_change(pk, log_id, 4)
        matter_log.date_change(pk, log_id, start_time, end_time)

        matter = Matter.objects.get(pk=pk)
        matter.start_time = start_time
        matter.end_time = end_time
        matter.matter_status = 4
        matter.save()
        return Response({"info": "确定排期成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([TrainningPermission, ])
    def trainning(self, request, pk=None, *args, **kwargs):
        """
        培训
        :param request:
        :param pk:
        :return:
        """
        verify = self.verify_teacher(request, pk)
        if verify == 0 and request.user.is_superuser is False:
            return Response({"error": "该问题的培训老师不是您,无权操作！"}, status=status.HTTP_400_BAD_REQUEST)
        data = self.request.data

        training_model = data.get("training_model")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        # 是否有遗留问题
        legacy_issue = data.get("legacy_issue")
        enclosure = data.get("enclosure")
        # 改动记录
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        matter_log = MatterLog()
        matter_log.status_change(pk, log_id, 8)
        matter_log.date_change(pk, log_id, start_time, end_time)

        matter = Matter.objects.get(pk=pk)
        matter.training_model = training_model
        matter.start_time = start_time
        matter.end_time = end_time
        matter.legacy_issue = legacy_issue
        matter.matter_status = 8
        matter.save()
        if enclosure != []:
            SimpleMatterViewsets.create_attachment(enclosure, "培训", 1, pk)
        return Response({"info": "培训完成"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([HandoverIssuesPermission, ])
    def handover_issues(self, request, pk=None, *args, **kwargs):
        """
        遗留问题交接
        :param request:
        :param pk:
        :return:
        """
        verify = self.verify_teacher(request, pk)
        if verify == 0 and request.user.is_superuser is False:
            return Response({"error": "该问题的培训老师不是您,无权操作！"}, status=status.HTTP_400_BAD_REQUEST)
        data = self.request.data
        dealing_person = data.get("dealing_person")
        problem_description = data.get("problem_description")
        enclosure = data.get("enclosure")

        dealing_person = self.get_user(dealing_person)
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        matter_log = MatterLog()
        matter_log.status_change(pk, log_id, 9)

        matter = Matter.objects.get(pk=pk)
        matter.dealing_person = dealing_person
        matter.problem_description = problem_description
        matter.matter_status = 9
        matter.save()
        if enclosure != []:
            SimpleMatterViewsets.create_attachment(enclosure, "遗留问题交接", 1, pk)

        return Response({"info": "遗留问题交接完成"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([IdentificationIssuesPermission, ])
    def identification_issues(self, request, pk=None, *args, **kwargs):
        """
        遗留问题确认
        :param request:
        :param pk:
        :return:
        """
        dealing_person = Matter.objects.get(pk=pk).dealing_person
        if dealing_person != request.user and request.user.is_superuser is False:
            return Response({"error": "您不是该问题的处理人，无权操作！"}, status=status.HTTP_400_BAD_REQUEST)
        data = self.request.data
        problem_description = data.get("problem_description")
        enclosure = data.get("enclosure")
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        matter_log = MatterLog()
        matter_log.status_change(pk, log_id, 10)
        matter_log.matter_describe(pk, log_id, problem_description)

        matter = Matter.objects.get(pk=pk)
        matter.problem_description = problem_description
        matter.matter_status = 10
        matter.save()
        if enclosure != []:
            atta = Attachment.objects.create(enclosure=enclosure, step_atta="遗留问题确认", atta_matter=matter)

        return Response({"info": "遗留问题确认成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([PersonnelAllocationPermission, ])
    def personnel_allocation(self, request, pk=None, *args, **kwargs):
        """
        调查人员分配
        :param request:
        :param pk:
        :return:
        """
        data = self.request.data
        investigador = data.get("investigador")
        # 获取用户实例
        investigador = self.get_user(investigador)
        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        matter_log = MatterLog()
        matter_log.status_change(pk, log_id, 11)

        matter = Matter.objects.get(pk=pk)
        matter.investigador = investigador
        matter.matter_status = 11
        matter.save()

        return Response({"info": "调查人员分配成功"}, status=status.HTTP_200_OK)

    @detail_route(['PUT'])
    @permission_classes([SatisfactionSurveyPermission, ])
    def satisfaction_survey(self, request, pk=None, *args, **kwargs):
        """
        满意度调查
        :param request:
        :param pk:
        :return:
        """
        data = self.request.data

        satisfaction_level = data.get("satisfaction_level")
        customer_feedback = data.get("customer_feedback")
        invest_start = data.get("invest_start")
        invest_end = data.get("invest_end")
        enclosure = data.get("enclosure")

        log_id = OpenStationViewSet.create_base_log(request, pk, "培训管理", 3)
        matter_log = MatterLog()
        matter_log.status_change(pk, log_id, 12)

        matter = Matter.objects.get(pk=pk)
        matter.satisfaction_level = satisfaction_level
        matter.customer_feedback = customer_feedback
        matter.invest_start = invest_start
        matter.invest_end = invest_end
        matter.matter_status = 12
        matter.save()
        if enclosure != []:
            # 新增附件
            SimpleMatterViewsets.create_attachment(enclosure, "满意度调查", 1, pk)

        return Response({"info": "满意度调查添加成功"}, status=status.HTTP_200_OK)


class SimpleMatterViewsets(viewsets.ModelViewSet):
    queryset = Matter.objects.all()

    def create_remark(self, request, content, mark_type, correlation_id):
        """
        新增备注
        :param request:
        :param content:
        :param mark_type:
        :param correlation_id:
        :return:
        """
        user = request.user
        remark_dict = {
            "user": user,
            "content": content,
            "mark_type": mark_type,
            "correlation_id": correlation_id
        }
        ret = RemarkEvolve.objects.create(**remark_dict)
        return ret

    @classmethod
    def get_martkdef(self, mark_type, correlation_id):
        """
        查看该关联对象的备注
        :param mark_type:
        :param correlation_id:
        :return:
        """
        mark_list = []
        mark = RemarkEvolve.objects.filter(correlation_id=correlation_id, mark_type=mark_type).order_by('-operationtime')
        for m in mark:
            user = m.user.last_name
            operationtime = m.operationtime
            content = m.content
            mark_list.append(
                {"user": user, "time": date_to_str(operationtime, format='%Y-%m-%d %H:%M:%S'), "content": content})
        mark_sort = sorted(mark_list, key=operator.itemgetter('time'), reverse=True)
        return mark_sort

    @classmethod
    def get_change_record(self, operationmodule, action, correlation_id):
        """
        获取改动记录
        :param operationmodule:
        :param action:
        :param correlation_id:
        :return:
        """
        # 获取改动记录
        query_params = {"operationmodule": operationmodule, "action": action, "title": correlation_id}
        train_log = OperateLog.objects.filter(**query_params)
        # 查询基础日志列表
        base_list = []
        for train in train_log:
            user = train.user.last_name
            time = date_to_str(train.operationtime, format='%Y-%m-%d %H:%M:%S')
            log_id = train.id
            query_detail = DetailLog.objects.filter(log_id_id=log_id)
            for v in query_detail:
                name = v.name
                old_value = v.old_value
                new_value = v.new_value
                base_list.append({"user": user, "time": time,
                                  "modify_list": {"name": name, "old_value": old_value, "new_value": new_value}})
        base_sort = sorted(base_list, key=operator.itemgetter('time'), reverse=True)
        return base_sort

    @list_route(['GET'])
    def get_staff(self, request):
        """
        获取指定分组的人员
        :param request:
        :return:
        """
        # 获取分组名称
        group_name = self.request.GET.get("group_name")
        if group_name == "培训管理经办人":
            # 经办人是项目实施顾问+客户运营顾问
            group_xm = Group.objects.get(name="项目实施顾问")
            group_kh = Group.objects.get(name="客户运营顾问")
            group_user = group_xm.user_set.values('id', 'last_name')
            group_khall = group_kh.user_set.values('id', 'last_name')
            group_user[0].update(group_khall[0])
        else:
            group = Group.objects.get(name=group_name)
            group_user = group.user_set.values('id', 'last_name')
        return Response(data=group_user, status=status.HTTP_200_OK)

    @list_route(['GET'])
    def training_methods(self, request):
        """
        培训管理-培训方式
        :param request:
        :return:
        """
        return Response(dict(TRAINING_METTART_METHOD))

    @list_route(['GET'])
    def matter_type(self, request):
        return Response(data=dict(MATTER_TYPE))

    @list_route(['GET'])
    def communicate_way(self, request):
        """
        沟通方式
        :param request:
        :return:
        """
        return Response(data=dict(WAY_MATTERCOMMUNICATE))

    @list_route(['GET'])
    def satisfaction_survey(self, request):
        """
        满意度调查
        :param request:
        :return:
        """
        return Response(data=dict(SATISFACTION_SURVEY))

    @list_route(['POST'])
    @permission_classes([RemarkPermission, ])
    def create_mark(self, request):
        """
        问题备注新增
        :param request:
        :return:
        """
        data = request.data
        content = data.get("content")
        matter = data.get("matter")
        self.create_remark(request, content, 2, matter)
        return Response(data={"info": "备注新增成功"}, status=status.HTTP_200_OK)

    @list_route(['GET'])
    def matter_export(self, request):
        """
        问题列表导出
        :param request:
        :return:
        """
        # 获取参数
        start_time = request.GET.get("start_time")
        end_time = request.GET.get("end_time")
        matter_flow = MatterFlowViewsets()
        query_params = {}

        if start_time:
            query_params.update({"start_time__gte": str_to_date(start_time)})
        if end_time:
            end_time = datetime_delta(str_to_date(end_time), days=1)
            query_params.update({"end_time__lte": end_time})

        name = "培训管理-客户培训"
        title_key = ["id", "company_name", "company_id", "deploy_way", "impl_cslt", "oper_supt", "commercial",
                     "training_instructors", "training_method", "training_contact", "start_time", "end_time",
                     "training_model"]
        title_value = ["id", "企业名称", "企业ID", "部署方式", "实施顾问", "运营顾问", "商务","培训讲师","培训方式",
                       "培训联系人","培训开始时间", "培训结束时间","培训模块"]
        title = dict(zip(title_key, title_value))
        content_list = []
        queryset = Matter.objects.filter(**query_params).values('id', 'matter_status', 'company_matter')
        # 如果查询不是空集
        if not queryset:
            content_list.append(dict(zip(title_key, [i-i for i in range(len(title_key))])))
            excl = Excel_export(filename=name, title=title, content=content_list)
            response = excl.export_csv()
            return response

        for query in queryset:
            id = query["id"]
            company_matter = query["company_matter"]
            dic_comstaion = matter_flow.get_comstaion(company_matter)
            train_dict = matter_flow.get_trainfo(id)
            query.update(dic_comstaion)
            query.update(train_dict)
            content_list.append(query)
        excl = Excel_export(filename=name, title=title, content=content_list)
        response = excl.export_csv()
        return response

    @detail_route(['GET'])
    def get_remark(self, request, pk=None, *args, **kwargs):
        mark_list = []
        mark = RemarkEvolve.objects.filter(correlation_id=pk, mark_type=2).order_by('-operationtime')
        for m in mark:
            user = m.user.last_name
            operationtime = m.operationtime
            content = m.content
            mark_list.append({"user": user, "time": date_to_str(operationtime, format='%Y-%m-%d %H:%M:%S'), "content": content})
        mark_sort = sorted(mark_list, key=operator.itemgetter('time'), reverse=True)
        # 获取改动记录
        query_params = {"operationmodule": "培训管理", "action": 3, "title": pk}
        train_log = OperateLog.objects.filter(**query_params)
        # 查询基础日志列表
        base_list = []
        for train in train_log:
            user = train.user.last_name
            time = date_to_str(train.operationtime, format='%Y-%m-%d %H:%M:%S')
            log_id = train.id
            query_detail = DetailLog.objects.filter(log_id_id=log_id)
            for v in query_detail:
                name = v.name
                old_value = v.old_value
                new_value = v.new_value
                base_list.append({"user": user, "time": time, "modify_list": {"name": name, "old_value": old_value, "new_value": new_value}})
        base_sort = sorted(base_list, key=operator.itemgetter('time'), reverse=True)
        remark = request.user.has_perm("add_remark")
        if remark is True or request.user.is_superuser is True:
            button = ["备注"]
        else:
            button = []
        return Response({"mark": mark_sort, "log": base_sort, "button_list": button}, status=status.HTTP_200_OK)

    @detail_route(['GET'])
    def return_count(self, request, pk=None, *args, **kwargs):
        data = {}
        button_list = ["创建产品配置"]
        matter_count = Matter.objects.all().filter(company_matter=pk).count()
        product_count = ProductConfig.objects.all().filter(khk_id=pk).count()
        create_train = request.user.has_perm("matter_train.add_create-train")
        if create_train == True or request.user.is_superuser:
            button_list.append("创建问题")
        data["matter"] = matter_count
        data["product"] = product_count
        data["button_list"] = button_list
        return Response(data=data, status=status.HTTP_200_OK)

    @classmethod
    def create_attachment(self, enclosure, step_atta, atta_type, correlation_id):
        """
        创建附件
        :param enclosure:
        :param step_atta:
        :param atta_type:
        :param correlation_id:
        :return:
        """
        atta_dict = {
            "enclosure": enclosure,
            "step_atta": step_atta,
            "atta_type": atta_type,
            "correlation_id": correlation_id
        }
        atta = Attachment.objects.create(**atta_dict)
        return 'ok'

    def notice_button(self, request, data):
        """
        告诉前端展示什么按钮
        当前状态                可以显示的按钮
        (1, "培训信息提交"),     分配讲师 驳回
        (2, "讲师分配完成"),     沟通培训需求
        (3, "驳回"),            再次申请
        (4, "培训需求确认完成"),  培训准备 待客户排期  客户终止培训
        (5, "培训准备完成"),      培训 待客户排期
        (6, "培训挂起"),         客户终止培训  确定客户排期
        (7, "终止培训"),         无
        (8, "培训完成"),         遗留问题交接
        (9, "交接完成"),         遗留问题确认
        (10, "遗留问题已确认"),   满意度调查，调查人员分配
        (11, "调查人员分配"),     满意度调查
        (12, "培训任务完成"),     无
        :param request:
        :return:
        """
        matter_class = MatterFlowViewsets()
        # 问题状态
        status = data.get("matter_status")

        # 问题经办人
        responsible = data.get("responsible")
        responsible = User.objects.get(pk=responsible)
        # 培训讲师 id
        training_instructors = data.get("training_instructors")
        # 问题处理人 id
        dealing_person = data.get("dealing_person")
        # 调查人员 id
        investigador = data.get("investigador")
        # 是否有遗留问题
        legacy_issue = data.get("legacy_issue")

        button_list = []
        if status == 1:
            p1 = request.user.has_perm("matter_train.change_distribution-lecturer")
            p2 = request.user.has_perm("matter_train.change_reject")
            if request.user.is_superuser:
                button_list = [{"name": "分配讲师"}, {"name": "驳回"}]
            else:
                if p1 == True:
                    button_list.append({"name": "分配讲师"})
                if p2 == True:
                    button_list.append({"name": "驳回"})
        if status == 2:
            p1 = request.user.has_perm("matter_train.change_communication-requirements")
            training_instructors = User.objects.get(pk=training_instructors)
            if (p1 == True and training_instructors == request.user) or request.user.is_superuser:
                button_list = [{"name": "沟通培训需求"}]
        if status == 3:
            p1 = request.user.has_perm("matter_train.add_create-train")
            if (p1 == True and responsible == request.user) or request.user.is_superuser:
                button_list = [{"name": "再次申请"}]
        elif status == 4:
            p1 = request.user.has_perm("matter_train.change_training-prepare")
            p2 = request.user.has_perm("matter_train.change_set-pending")
            p3 = request.user.has_perm("matter_train.change_termination-training")
            training_instructors = User.objects.get(pk=training_instructors)

            if request.user.is_superuser:
                button_list = [{"name": "培训准备"}, {"name": "待客户排期"}, {"name": "客户终止培训"}]
            else:
                if p1 == True and training_instructors == request.user:
                    button_list.append({"name": "培训准备"})
                if p2 == True and training_instructors == request.user:
                    button_list.append({"name": "待客户排期"})
                if p3 == True and training_instructors == request.user:
                    button_list.append({"name": "客户终止培训"})
        elif status == 5:
            p1 = request.user.has_perm("matter_train.change_trainning")
            p2 = request.user.has_perm("matter_train.change_set-pending")
            training_instructors = User.objects.get(pk=training_instructors)
            if request.user.is_superuser:
                button_list = [{"name": "培训"}, {"name": "待客户排期"}]
            else:
                if p1 == True and training_instructors == request.user:
                    button_list.append({"name": "培训"})
                if p2 == True and training_instructors == request.user:
                    button_list.append({"name": "待客户排期"})
        elif status == 6:
            p1 = request.user.has_perm("matter_train.change_termination-training")
            p2 = request.user.has_perm("matter_train.change_determine-scheduling")
            training_instructors = User.objects.get(pk=training_instructors)
            if request.user.is_superuser:
                button_list = [{"name": "客户终止培训"}, {"name": "确定排期"}]
            else:
                if p1 == True and training_instructors == request.user:
                    button_list.append({"name": "客户终止培训"})
                if p2 == True and training_instructors == request.user:
                    button_list.append({"name": "确定排期"})
        elif status == 8:
            # 如果有遗留问题
            training_instructors = User.objects.get(pk=training_instructors)
            if legacy_issue == 1:
                p1 = request.user.has_perm("matter_train.change_handover-issues")
                if (p1 == True and training_instructors == request.user) or request.user.is_superuser:
                    button_list = [{"name": "遗留问题交接"}]
            # 如果没有遗留问题，跳过问题交接过程
            else:
                p1 = request.user.has_perm("matter_train.change_satisfaction-survey")
                p2 = request.user.has_perm("matter_train.change_personnel-allocation")
                if request.user.is_superuser:
                    button_list = [{"name": "满意度调查"}, {"name": "调查人员分配"}]
                else:
                    if p1 == True:
                        button_list.append({"name": "满意度调查"})
                    if p2 == True:
                        button_list.append({"name": "调查人员分配"})
        elif status == 9:
            dealing_person = User.objects.get(pk=dealing_person)
            p1 = request.user.has_perm("matter_train.change_identification-issues")
            if (p1 == True and dealing_person == request.user) or request.user.is_superuser:
                button_list = [{"name": "遗留问题确认"}]
        elif status == 10:
            p1 = request.user.has_perm("matter_train.change_satisfaction-survey")
            p2 = request.user.has_perm("matter_train.change_personnel-allocation")
            if request.user.is_superuser:
                button_list = [{"name": "满意度调查"}, {"name": "调查人员分配"}]
            else:
                if p1 == True:
                    button_list.append({"name": "满意度调查"})
                if p2 == True:
                    button_list.append({"name": "调查人员分配"})
        elif status == 11:
            p1 = request.user.has_perm("matter_train.change_satisfaction-survey")
            investigador = User.objects.get(pk=investigador)

            if (p1 == True and request.user == investigador) or request.user.is_superuser:
                button_list = [{"name": "满意度调查"}]
        return button_list
