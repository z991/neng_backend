import csv
import codecs
import datetime

from django.db.models import Sum
from rest_framework import status
from django.http import HttpResponse
from libs.excel_base import Excel_export
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import list_route
from rest_framework.viewsets import GenericViewSet
from applications.workorder_manage.models import CompanyInfo, OpenStationManage
from applications.data_manage.models import InquiriesData, VistorData, OperatingRecord, \
    RefactoringConsultingAndVisitors
from applications.setup.permissions import ChannelDataPermission, IndustrySiteDataPermission
from ldap_server.configs import CHANNEL_CHOICES, DEPLOY_WAYS, OPERATE_ACTION_CHOICES, REFACTORING_CHANNEL_CHOICES
from libs.datetimes import date_to_str, datetime_delta, str_to_date

today = datetime.date.today()
deploy_dict = dict(DEPLOY_WAYS)


class ChannelData(GenericViewSet):
    queryset = VistorData.objects.all().order_by('-id')
    permission_classes = [ChannelDataPermission, IndustrySiteDataPermission]

    def get_queryset(self):
        queryset = VistorData.objects.all()
        # 约束日期
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        # if not (start_date and end_date):
        #     return Response({'error': '请输入开始时间和结束时间！！！'}, status=status.HTTP_400_BAD_REQUEST)

        if start_date:  # 开始时间查询
            queryset = queryset.filter(date__gte=start_date)
        if end_date:  # 结束时间查询
            queryset = queryset.filter(date__lte=end_date)

        return queryset

    # 设置（补充0）默认值
    def default_data(self, data_dict, start_date, end_date):
        date_list = self.handle_get_date(start_date, end_date)
        # 进行 缺省数据补0 操作
        for items in data_dict.values():
            for date in date_list:
                date = date_to_str(date)
                if date not in list(items.keys()):
                    items.update({date: 0})
        return data_dict

    # 实施渠道数据格式转换
    def handle_channel_data(self, channel_list, channel_total, start_date, end_date):
        data_dict = {}
        for each in channel_total:
            inquires_num = each.get('inquires_num')
            channel = each.get('channel')
            date = date_to_str(each.get('date'))
            if data_dict.get(channel):
                data_dict[channel].update({date: inquires_num})
            else:
                data_dict[channel] = {date: inquires_num}

        # 缺省数据补充默认值
        data_dict = self.default_data(data_dict, start_date, end_date)

        # 把数据按时间排序,给前端
        big_list = []
        for channel, item in data_dict.items():
            name = channel_list[channel]
            new_list = sorted(item.keys())
            big_list.append({'name': name, 'data': [item[i] for i in new_list]})
        return big_list

    # 获取时间列表 [2018-08-29, 2018-08-30, 2018-08-31] 时间对象列表
    def handle_get_date(self, start_date, end_date):
        start_date = str_to_date(start_date)
        end_date = str_to_date(end_date)
        date_list = []
        day_number = (end_date - start_date).days
        for d in range(day_number):
            date_list.append(datetime_delta(start_date, days=int(d)))
        return date_list

    # 渠道数据获取
    @list_route(methods=['get'])
    def get_channel(self, request):
        # 咨询量查询集
        consult_queryset = InquiriesData.objects.all()
        # 访客量查询集
        visitors_queryset = VistorData.objects.all()

        # 约束日期 ========================  参数  =============================
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if not (start_date and end_date):
            return Response({'error': '请输入开始时间和结束时间！！！'}, status=status.HTTP_400_BAD_REQUEST)

        # 渠道参数
        channellist = request.GET.getlist('channel', '')
        if len(channellist) > 3:
            return Response({'error': '行业参数超过三个'}, status=status.HTTP_400_BAD_REQUEST)

        # 运营指标 经典版访客量没有区分渠道
        # index = request.GET.get('index', 0)

        # 行业
        industry = request.GET.get('industry', '')

        # 部署方式
        deploy = request.GET.get('deploy', '')

        # 渠道列表
        channel_list = dict(CHANNEL_CHOICES)

        data = {'consult': 0, 'visitors': 0, 'bread': [], 'broken_line': [], 'form': []}
        params = {}
        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date
        if deploy:
            params['deploy_way'] = deploy
        if industry:
            params['industry'] = industry

        consult_queryset = consult_queryset.filter(**params)

        # 添加表格数据 ===========================================
        # 1. 获取咨询量 访客量没有区分渠道
        from_inquires_data = consult_queryset.values('channel')\
            .annotate(inquires_num=Sum('inquires_num'))\
            .values_list('channel', 'inquires_num')

        for ins in from_inquires_data:
            channel_name = channel_list[ins[0]]
            consult = int(ins[1])
            data['form'].append({'channel': channel_name, 'consult': consult, 'visitors': 0})

        # 获取部署方式列表
        deploy_dict = dict(DEPLOY_WAYS)
        deploy_list = []
        for key, value in deploy_dict.items():
            deploy_list.append({'name': value, 'value': key})

        # 参数可以有一个或者多个
        if isinstance(channellist, list):
            consult_queryset = consult_queryset.filter(channel__in=channellist)

        # 咨询量渠道数据 ==================================================
        channel_total = consult_queryset.values('channel', 'date')\
            .annotate(inquires_num=Sum('inquires_num'))\
            .values('channel', 'inquires_num', 'date')
        # 总数据格式 分别为饼图(bread)和折线图(broken_line) ==============
        small_list = self.handle_channel_data(channel_list, channel_total, start_date, end_date)
        # 折线图(broken_line) =============
        data['broken_line'] = small_list
        # 饼图(bread)  =================
        for inner_item in small_list:
            if isinstance(inner_item, dict):
                data['bread'].append({'name': inner_item['name'], 'value': sum(inner_item['data'])})

        # 统计总量 ===============================================
        inquires_total_data = consult_queryset.values('date').annotate(num=Sum('inquires_num'))\
            .values_list('num', flat=True)
        # 咨询总量
        for number in inquires_total_data:
            data['consult'] += number
        visitor_total_data = visitors_queryset.filter(**params).values('date').annotate(num=Sum('visitor_num'))\
            .values_list('num', flat=True)
        # 访客总量
        for number in visitor_total_data:
            data['visitors'] += number
        # 没有部署方式参数 默认添加部署方式下拉列表 ========================
        if not deploy:
            data['deploy_list'] = deploy_list
        # 没有参数 返回默认数据和渠道下拉列表
        if not channellist:
            data['channel_list'] = channel_list
        return Response(data=data, status=status.HTTP_200_OK)

    # 行业数据获取
    @list_route(['GET'])
    def get_industry(self, request):
        # 咨询量查询集
        consult_queryset = InquiriesData.objects.all()
        # 访客量查询集
        visitors_queryset = VistorData.objects.all()

        # 约束日期 ========================  参数  =============================
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if not (end_date and start_date):
            return Response({'error': '请输入开始时间和结束时间！！！'}, status=status.HTTP_400_BAD_REQUEST)

        # 行业
        industry = request.GET.get('industry', '')
        # 部署方式
        deploy = request.GET.get('deploy', '')
        # 运营指标
        index = request.GET.get('index', 0)

        params = {}
        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date
        if industry:
            params['industry'] = industry
        if deploy:
            params['deploy_way'] = deploy

        # 数据 总格式
        data = {'consult': 0, 'visitors': 0, 'bread': [], 'broken_line': [], 'different_bread': []}

        # 部署方式列表
        deploy_dict = dict(DEPLOY_WAYS)
        deploy_list = []
        for a, b in deploy_dict.items():
            deploy_list.append({'name': b, 'value': a})

        consult_queryset = consult_queryset.filter(**params)
        visitors_queryset = visitors_queryset.filter(**params)

        # 折线图数据 ===================================================
        # [{'name': '行业1', 'data': [48672, 42112, 1003]}, {}, {}......]
        consult_line_data = consult_queryset.values('industry').annotate(consult=Sum('inquires_num'))\
            .values_list('industry', 'consult', 'date')

        visitor_line_data = visitors_queryset.values('industry').annotate(visitor=Sum('visitor_num')) \
            .values_list('industry', 'visitor', 'date')

        # 运营指标index  默认index为0(咨询量)  index为1(访客量)
        small_data = visitor_line_data if int(index) else consult_line_data
        line_data = self.handle_industry(small_data, start_date, end_date)
        data['broken_line'] = line_data

        # 南丁格尔图数据 ====================只看咨询量=============================
        different_bread_data = self.handle_industry(consult_line_data, start_date, end_date)
        for each in different_bread_data:
            total = sum(each.pop('data'))
            each['value'] = total

        data['different_bread'] = different_bread_data
        # 饼图数据 ===================================================
        bread_data = consult_queryset.values('deploy_way').annotate(consult=Sum('inquires_num'))\
            .values_list('deploy_way', 'consult')
        inner_list = []
        for deploy_name, consult_value in bread_data:
            inner={}
            inner['name'] = deploy_dict[deploy_name]
            inner['value'] = consult_value
            inner_list.append(inner)

        data['bread'] = inner_list
        # 顶部总量数据 ===================================================
        for item in different_bread_data:
            data['consult'] += int(item.get('value', 0))
        # 关于访客量: 如果index为1 直接用折线图数据 否则查数据库
        if int(index):
            data['visitors'] = sum([sum(item.get('data')) for item in line_data])
        else:
            total = visitors_queryset.aggregate(visitor=Sum('visitor_num'))
            if not total.get('visitor'):
                total = {'visitor': 0}
            data['visitors'] = total.get('visitor', 0)
        # 没有部署方式参数 默认添加部署方式下拉列表
        if not deploy:
            data['deploy_list'] = deploy_list
        return Response(data=data, status=status.HTTP_200_OK)

    # 实施行业数据格式转换
    def handle_industry(self, data, start_date, end_date):
        data_dict = {}
        for each in data:
            inquires_num = each[1]
            industry = each[0]
            date = date_to_str(each[2])
            if data_dict.get(industry):
                data_dict[industry].update({date: inquires_num})
            else:
                data_dict[industry] = {date: inquires_num}

        # 缺省数据补充默认值
        data_dict = self.default_data(data_dict, start_date, end_date)

        # 把数据按时间排序,给前端
        big_list = []
        for industry, item in data_dict.items():
            new_list = sorted(item.keys())
            big_list.append({'name': industry, 'data': [item[i] for i in new_list]})
        return big_list

    # 站点运营指标变化趋势
    @list_route(['GET'])
    def get_station_number(self, request):
        # 约束日期
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if not (end_date and start_date):
            return Response({'error': '请输入开始时间和结束时间！！！'}, status=status.HTTP_400_BAD_REQUEST)
        # 部署方式
        deploy = request.GET.get('deploy', '')
        # 运营指标
        action = request.GET.get('action', '')
        industry = request.GET.get('industry', '')

        params = {}
        action_list = list(dict(OPERATE_ACTION_CHOICES).values())
        action_list.remove('新增产品')
        action_dict = dict(OPERATE_ACTION_CHOICES)
        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date
        if deploy:
            params['deploy_way'] = deploy
        if industry:
            params['industry'] = industry
        if action:
            params['action'] = action
            action_list = [dict(OPERATE_ACTION_CHOICES)[int(action)]]
        total = OperatingRecord.objects.all().filter(**params).exclude(action=3).values('action', 'date') \
            .annotate(total=Sum('num')).values('action', 'date', 'total')

        days = (str_to_date(end_date) - str_to_date(start_date)).days + 1
        a = {}
        for j in action_list:
            a.update({j: []})
            for i in range(days):
                a[j].append(0)

        for each in total:
            index = int((each['date'] - str_to_date(start_date)).days)
            a[action_dict[each['action']]][index] = each['total']

        data = []
        for key, value in a.items():
            data.append({'name': key, 'data': value})
        return Response(data=data, status=status.HTTP_200_OK)

    # 站点总数变化趋势
    @list_route(['GET'])
    def get_station_total(self, request):
        """
        站点变化趋势计算原理:
        total = 基站点数量+净增长站点数量
        """
        # 约束日期
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        industry = request.GET.get('industry', '')
        if not (end_date and start_date):
            return Response({'error': '请输入开始时间和结束时间！！！'}, status=status.HTTP_400_BAD_REQUEST)

        params = {}
        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date
        if industry:
            params['industry'] = industry
        # 上线了 时间小于统计开始时间 经典站点 计算基站点数量
        start_total = OpenStationManage.objects.all().filter(online_status=1, updated_at__lt=start_date,
                                                             station_info__classify=1) \
            .aggregate(total=Sum('is_enable'))

        # 计算净增长站点数量
        total = OperatingRecord.objects.all().filter(**params).filter(action__in=[4, 5]) \
            .values('action', 'date').annotate(total=Sum('num')).values('action', 'date', 'total')
        start_number = int(start_total.get('total', 0))
        days = (str_to_date(end_date) - str_to_date(start_date)).days + 1
        a = []
        for i in range(days):
            a.append(0)
        for each in total:
            index = (each['date'] - str_to_date(start_date)).days
            if each['action'] == 4:
                a[index] += int(each['total'])
            if each['action'] == 5:
                a[index] -= int(each['total'])
        data = {'name': 'total', 'data': []}
        for num in a:
            data['data'].append(start_number + num)
        return Response(data=data, status=status.HTTP_200_OK)

    # 站点运营指标总数表
    @list_route(['GET'])
    def get_station_title(self, request):
        queryset = OperatingRecord.objects.all().order_by('-id')
        start_date = str_to_date(request.GET.get('start_date'))
        end_date = str_to_date(request.GET.get('end_date'))
        industry = request.GET.get('industry', '')
        deploy_way = request.GET.get('depoly', '')
        params = {}

        if start_date:
            params['date__gte'] = start_date
        if end_date:
            params['date__lte'] = end_date

        if industry:
            params['industry'] = industry
        if deploy_way:
            params['deploy_way'] = deploy_way
        queryset = queryset.filter(**params)

        ret = {}
        online_set = queryset.exclude(action=3).extra(select={'name': 'action'}).defer('action') \
            .values('name').annotate(value=Sum('num')).values('name', 'value')

        opt_dict = dict(OPERATE_ACTION_CHOICES)
        online_dict = {}
        for online in online_set:
            if opt_dict[online["name"]] not in online_dict:
                online_dict.update({opt_dict[online["name"]]: online["value"]})
            else:
                k = int(online["name"])
                key = opt_dict[k]
                online_dict[key] += online["value"]

        # 对其他状态没有数据进行补零
        for op in opt_dict:
            if opt_dict[op] not in online_dict:
                online_dict[opt_dict[op]] = 0
        online_dict.pop("新增产品")

        ret['name'] = list(online_dict.keys())
        ret['data'] = list(online_dict.values())
        return Response(data=ret, status=status.HTTP_200_OK)

    # 企业导出接口
    @list_route(methods=['get'])
    def derive_enterprise(self, request):
        company_id = request.GET.get('company_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        version = request.GET.get('version', 0)
        name = 'enterpriseData'
        if company_id:
            name = CompanyInfo.objects.all().filter(classify=version)\
                .filter(open_station__station_info__company_id=company_id)\
                .values_list('company_name', flat=True)
            if not name:
                name = 'unknownSite'

        title = {'date': '时间', 'uv': '访客量', 'pv': '咨询量'}
        content_list = []

        params = {}
        if start_date:
            params["date__gte"] = str_to_date(start_date)
        if end_date:
            params["date__lte"] = str_to_date(end_date)
        if company_id:
            params['company_id'] = company_id

        if int(version) == 1:
            re_data = RefactoringConsultingAndVisitors.objects.all().filter(**params).values('date')\
                .annotate(con=Sum('valid_consulting'), in_con=Sum('invalid_consulting'), uv=Sum('unique_vistor'))\
                .values('date', 'con', 'in_con', 'uv')
            if not re_data:
                title_key = title.keys()
                content_list.append(dict(zip(title_key, [i-i for i in range(len(title_key))])))
            for i in re_data:
                inner_data = [i.get('date'), i.get('uv'), int(i.get('con')) + int(i.get('in_con'))]
                inner_dict = dict(zip(title.keys(), inner_data))
                content_list.append(inner_dict)
        else:
            query_con = InquiriesData.objects.all().filter(**params)
            query_vis = VistorData.objects.all().filter(**params)
            consult = query_con.values('date').annotate(consult=Sum('inquires_num'))\
                .values('date', 'consult')
            visitor = query_vis.values('date').annotate(visitor=Sum('visitor_num'))\
                .values('date', 'visitor')
            if not (consult and visitor):
                title_key = title.keys()
                content_list.append(dict(zip(title_key, [i - i for i in range(len(title_key))])))
            long = consult
            short = visitor
            if len(visitor) >= len(consult):
                long = visitor
                short = consult

            for item in long:
                for each in short:
                    if item['date'] == each['date']:
                        v_value = item.get('visitor') if item.get('visitor') else each.get('visitor')
                        c_value = item.get('consult') if item.get('consult') else each.get('consult')
                        content_list.append({'date': item['date'], 'uv': v_value, 'pv': c_value})

        # title = {"siteid": "企业id", "name": "企业名称"}
        # content = [{"siteid": "kf_123", "name": "哈喽"}, {"siteid": "kf_1234", "name": "哈喽1"}]
        excl = Excel_export(filename=name, title=title, content=content_list)
        response = excl.export_csv()

        return response

    # 节点导出接口
    @list_route(['GET'])
    def derive_grid(self, request):
        grid = request.GET.get('grid')
        deploy = request.GET.get('deploy')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        version = request.GET.get('version', 0)

        params = {}
        name = 'gridData'
        if grid:
            params['grid'] = grid
            name = grid
        if start_date:
            params["date__gte"] = str_to_date(start_date)
        if end_date:
            params["date__lte"] = str_to_date(end_date)

        title = {'date': '时间', 'deploy': '部署方式', 'grid': '节点', 'uv': '访客量', 'pv': '咨询量'}
        content_list = []

        if int(version) == 1:
            if deploy:
                params['deploy'] = deploy
            re_data = RefactoringConsultingAndVisitors.objects.all().filter(**params)\
                .values('date', 'grid')\
                .annotate(con=Sum('valid_consulting'), in_con=Sum('invalid_consulting'), uv=Sum('unique_vistor'))\
                .values('date', 'deploy', 'grid', 'con', 'in_con', 'uv')
            if not re_data:
                title_key = title.keys()
                content_list.append(dict(zip(title_key, [i - i for i in range(len(title_key))])))
            for i in re_data:
                inner_data = [i.get('date'), deploy_dict.get(int(i.get('deploy'))), i.get('grid'), i.get('uv'),
                                 int(i.get('con'))+int(i.get('in_con'))]
                inner_dict = dict(zip(title.keys(), inner_data))
                content_list.append(inner_dict)
        else:
            if deploy:
                params['deploy_way'] = deploy
            query_con = InquiriesData.objects.all().filter(**params)
            query_vis = VistorData.objects.all().filter(**params)
            consult = query_con.values('date', 'grid').annotate(consult=Sum('inquires_num')) \
                .values('date', 'consult', 'grid', 'deploy_way')
            visitor = query_vis.values('date', 'grid').annotate(visitor=Sum('visitor_num')) \
                .values('date', 'visitor', 'grid', 'deploy_way')

            if not (consult and visitor):
                title_key = title.keys()
                content_list.append(dict(zip(title_key, [i - i for i in range(len(title_key))])))

            long = consult
            short = visitor
            if len(visitor) >= len(consult):
                long = visitor
                short = consult

            for item in long:
                for each in short:
                    if item['date'] == each['date'] and item['grid'] == each['grid'] \
                            and item['deploy_way'] == each['deploy_way']:
                        v_value = item.get('visitor') if item.get('visitor') else each.get('visitor')
                        c_value = item.get('consult') if item.get('consult') else each.get('consult')
                        content_list.append({'date': item['date'], 'deploy': deploy_dict.get(int(item['deploy_way'])),
                                  'grid': item['grid'], 'uv': v_value, 'pv': c_value})

        excl = Excel_export(filename=name, title=title, content=content_list)
        response = excl.export_csv()
        return response

    # 渠道导出接口
    @list_route(['GET'])
    def derive_channel(self, request):
        channel = request.GET.get('channel')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        deploy = request.GET.get('deploy')
        industry = request.GET.get('industry')
        version = request.GET.get('version', 0)

        deploy_dict = dict(DEPLOY_WAYS)
        re_channel = dict(REFACTORING_CHANNEL_CHOICES)
        channel_dict = dict(CHANNEL_CHOICES)

        name = 'enterpriseData'
        if channel:
            name = channel
            if not name:
                name = 'unknownSite'

        title = {}
        content_list = []

        params = {}
        if start_date:
            params["date__gte"] = str_to_date(start_date)
        if end_date:
            params["date__lte"] = str_to_date(end_date)
        if industry:
            params['industry'] = industry
        if channel:
            params['channel'] = channel

        # 只要选择了行业或者部署方式就直接用  没有选择就显示全部
        if int(version) == 1:
            title_row = ['时间', '部署方式', '行业'] + list(re_channel.values())
            title_key = ['date', 'deploy', 'industry'] + list(re_channel.values())
            title = dict(zip(title_key, title_row))
            if deploy:
                params['deploy'] = deploy
            re_data = RefactoringConsultingAndVisitors.objects.all().filter(**params).values('date', 'channel')\
                .annotate(con=Sum('valid_consulting'), in_con=Sum('invalid_consulting'))\
                .values('date', 'channel', 'con', 'in_con')
            if not re_data:
                content_list.append(dict(zip(title_key, [i - i for i in range(len(title_key))])))

            re_dict = {}
            for item in re_data:
                key = date_to_str(item['date'])
                if re_dict.get(key):
                    re_dict[key].append(item)
                else:
                    re_dict[key] = [item]

            for date_key, each in re_dict.items():
                write_list = {'date': date_key, 'industry': '全部', 'deploy': '全部'}
                if industry:
                    write_list['industry'] = industry
                if deploy:
                    write_list['deploy'] = deploy_dict.get(int(deploy))
                write_list.update(dict(zip(re_channel.values(), [zero-zero for zero in range(len(re_channel))])))
                for i in each:
                    channel = re_channel.get(i.get('channel'))
                    value = int(i.get('con')) + int(i.get('in_con'))
                    write_list[channel] = value

                content_list.append(write_list)
        else:
            title_row = ['时间', '部署方式', '行业'] + list(channel_dict.values())
            title_key = ['date', 'deploy', 'industry'] + list(channel_dict.values())
            title = dict(zip(title_key, title_row))
            if deploy:
                params['deploy_way'] = deploy
            con_data = InquiriesData.objects.all().filter(**params).values('date', 'channel')\
                .annotate(num=Sum('inquires_num'))\
                .values('date', 'channel', 'num')
            if not con_data:
                content_list.append(dict(zip(title_key, [i - i for i in range(len(title_key))])))

            re_dict = {}
            for item in con_data:
                key = date_to_str(item['date'])
                if re_dict.get(key):
                    re_dict[key].append(item)
                else:
                    re_dict[key] = [item]

            for date_key, each in re_dict.items():
                write_list = {'date': date_key, 'industry': '全部', 'deploy': '全部'}
                if industry:
                    write_list['industry'] = industry
                if deploy:
                    write_list['deploy'] = deploy_dict.get(int(deploy))
                write_list.update(dict(zip(channel_dict.values(), [zero-zero for zero in range(len(channel_dict))])))
                for i in each:
                    channel = channel_dict.get(i.get('channel'))
                    value = i.get('num')
                    write_list[channel] = value

                content_list.append(write_list)

        excl = Excel_export(filename=name, title=title, content=content_list)
        response = excl.export_csv()
        return response

    # 站点导出接口
    @list_route(['GET'])
    def derive_site(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        deploy = request.GET.get('deploy')
        industry = request.GET.get('industry')

        action_dict = dict(OPERATE_ACTION_CHOICES)
        # 去除续费客户
        action_dict.pop(3)
        name = 'siteData'

        title_row = ['时间', '部署方式', '行业'] + list(action_dict.values())
        title_key = ['date', 'deploy', 'industry'] + list(action_dict.values())
        title = dict(zip(title_key, title_row))
        content_list = []

        params = {}
        if start_date:
            params["date__gte"] = str_to_date(start_date)
        if end_date:
            params["date__lte"] = str_to_date(end_date)
        if industry:
            params['industry'] = industry
        if deploy:
            params['deploy_way'] = deploy

        site_data = OperatingRecord.objects.all().filter(**params).values('date', 'action', 'num')

        if not site_data:
            content_list.append(dict(zip(title_key, [i - i for i in range(len(title_key))])))

        re_dict = {}
        for item in site_data:
            key = date_to_str(item.get('date'))
            if re_dict.get(key):
                re_dict[key].append(item)
            else:
                re_dict[key] = [item]
        for date_key, each in re_dict.items():
            write_list = {'date': date_key, 'industry': '全部', 'deploy': '全部'}
            if industry:
                write_list['industry'] = industry
            if deploy:
                write_list['deploy'] = deploy_dict.get(int(deploy))
            write_list.update(dict(zip(action_dict.values(), [zero - zero for zero in range(len(action_dict))])))
            for i in each:
                action = action_dict.get(i.get('action'))
                write_list[action] = i.get('num')

            content_list.append(write_list)

        excl = Excel_export(filename=name, title=title, content=content_list)
        response = excl.export_csv()
        return response

    # 行业导出接口
    @list_route(['GET'])
    def derive_industry(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        deploy = request.GET.get('deploy')
        industry = request.GET.get('industry')
        version = request.GET.get('version', 0)

        name = 'siteData'

        title_row = ['时间', '部署方式', '行业', '咨询量', '访客量']
        title_key = ['date', 'deploy', 'industry', 'pv', 'uv']
        title = dict(zip(title_key, title_row))
        content_list = []

        params = {}
        if start_date:
            params["date__gte"] = str_to_date(start_date)
        if end_date:
            params["date__lte"] = str_to_date(end_date)
        if industry:
            params['industry'] = industry

        if int(version) == 1:
            if deploy:
                params['deploy'] = deploy

            re_data = RefactoringConsultingAndVisitors.objects.all().filter(**params)\
                .values('date')\
                .annotate(pv=Sum('valid_consulting'), in_pv=Sum('invalid_consulting'), uv=Sum('unique_vistor'))\
                .values('date', 'pv', 'uv', 'in_pv')

            if not re_data:
                content_list.append(dict(zip(title_key, [i - i for i in range(len(title_key))])))

            re_dict = {}
            for item in re_data:
                key = date_to_str(item.get('date'))
                if re_dict.get(key):
                    re_dict[key].append(item)
                else:
                    re_dict[key] = [item]
            for date_key, each in re_dict.items():
                write_list = {'date': date_key, 'industry': '全部', 'deploy': '全部', 'pv': 0, 'uv': 0}
                if industry:
                    write_list['industry'] = industry
                if deploy:
                    write_list['deploy'] = deploy_dict.get(int(deploy))

                for i in each:
                    pv = int(i.get('pv')) + int(i.get('in_pv'))
                    write_list['uv'] = int(i.get('uv'))
                    write_list['pv'] = pv

                content_list.append(write_list)
        else:
            if deploy:
                params['deploy_way'] = deploy

            pv_data = InquiriesData.objects.all().filter(**params).values('date')\
                .annotate(pv=Sum('inquires_num')).values('date', 'pv')
            uv_data = VistorData.objects.all().filter(**params).values('date')\
                .annotate(uv=Sum('visitor_num')).values('date', 'uv')

            if not (uv_data and pv_data):
                content_list.append(dict(zip(title_key, [i - i for i in range(len(title_key))])))

            long = pv_data
            short = uv_data
            if len(uv_data) >= len(pv_data):
                long = uv_data
                short = pv_data

            for item in long:
                date_value = date_to_str(item['date'])
                for each in short:
                    if item['date'] == each['date']:
                        v_value = item.get('uv') if item.get('uv') else each.get('uv')
                        c_value = item.get('pv') if item.get('pv') else each.get('pv')
                        write_list = {'date': date_value, 'industry': '全部', 'deploy': '全部', 'pv': 0, 'uv': 0}
                        if industry:
                            write_list['industry'] = industry
                        if deploy:
                            write_list['deploy'] = deploy_dict.get(int(deploy))

                        write_list['uv'] = v_value
                        write_list['pv'] = c_value
                        content_list.append(write_list)

        excl = Excel_export(filename=name, title=title, content=content_list)
        response = excl.export_csv()
        return response


@api_view(['GET'])
def test_channel(request):
    # 更新今天和昨天的重构咨询访客数据
    from applications.data_manage.task import fetch_channel_haier
    data = fetch_channel_haier()
    return Response(data, status=status.HTTP_200_OK)
