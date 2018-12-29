import datetime
from django.db.models import Sum, F, Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes

from applications.data_manage.models import OnlineProductData, \
    RefactoringConsultingAndVisitors, OperatingRecord, InquiriesData, VistorData
from applications.production_manage.models import Grid
from applications.data_manage.models import InquiriesData
from applications.workorder_manage.models import CompanyInfo, OpenStationManage
from libs.datetimes import str_to_date, dates_during
from ldap_server.configs import DEPLOY_WAYS, REFACTORING_CHANNEL_CHOICES, CHANNEL_CHOICES
from libs.inquires.refactor_channel_consulting import get_site_company
from applications.log_manage.models import OperateLog
from applications.setup.permissions import DataOverviewPermission, CompanyDataPermission, GridDataPermission


channal_dict = dict(REFACTORING_CHANNEL_CHOICES)
jdchannal_dict = dict(CHANNEL_CHOICES)
deploy_dict = dict(DEPLOY_WAYS)


# 首页上面4个数据块展示
@api_view(['GET'])
@permission_classes([DataOverviewPermission, ])
def home_top(request):
    op = OpenStationManage.objects.filter(station_info__classify=2).count()

    data = []
    # 总量查询集
    total_base_query = RefactoringConsultingAndVisitors.objects.all()
    i_dict = {}
    valid_con = total_base_query.aggregate(consulting_total=Sum('valid_consulting'))
    invalid_con = total_base_query.aggregate(invalid_consulting=Sum('invalid_consulting'))
    valid_vis = total_base_query.aggregate(valid_visitors=Sum('unique_vistor'))
    i_dict["name"] = "历史重构咨询量"
    i_dict["total"] = int(valid_con.get('consulting_total', 0)) + int(invalid_con.get('invalid_consulting', 0))
    data.append(i_dict)

    v_dict = {}
    v_dict["name"] = "历史重构访客量"
    v_dict["total"] = int(valid_vis.get('valid_visitors', 0))
    data.append(v_dict)

    o_dict = {}
    o_dict["name"] = "历史重构站点数量"
    o_dict["total"] = op
    data.append(o_dict)
    OperateLog.create_log(request)
    return Response(data=data, status=status.HTTP_200_OK)


# 首页其余数据展示
@api_view(['GET'])
@permission_classes([DataOverviewPermission, ])
def home_rest(request):

    params = dict()

    from_date = str_to_date(request.GET.get("from_date", "").strip())
    to_date = str_to_date(request.GET.get("to_date", "").strip())

    if from_date and to_date:
        params["date__gte"] = from_date
        params["date__lte"] = to_date

    # 总得咨询量
    all_con = RefactoringConsultingAndVisitors.objects.filter(**params).values('valid_consulting', 'invalid_consulting')
    all_set = all_con.aggregate(valid=Sum('valid_consulting'), unvalid=Sum('invalid_consulting'))

    valid = all_set.get("valid", 0)
    unvalid = all_set.get("unvalid", 0)
    if valid == None:
        valid = 0
    if unvalid == None:
        unvalid = 0

    total_con = int(valid) + int(unvalid)

    # 咨询量和访客量数据
    conz_list = []
    visz_list = []

    consulting = RefactoringConsultingAndVisitors.objects.all(). \
                filter(**params).values('date').annotate(
                ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting"),
                ef_vis=Sum('unique_vistor')). \
                values_list('date', 'ef_conf', 'in_conf', 'ef_vis')

    # 初步获取咨询量和访客量
    conz_dict, visz_dict = initial_dict(consulting)

    # 补0数据
    conz_date = patch_zero(from_date, to_date, conz_dict)
    conz_list.append({'name': "咨询量", 'data': conz_date.values()})

    # 补齐没有访客量的日期的数据
    visz_date = patch_zero(from_date, to_date, visz_dict)
    visz_list.append({'name': "访客量", 'data': visz_date.values()})

    # 咨询量渠道占比
    channal_list = []
    channal_set = RefactoringConsultingAndVisitors.objects.all(). \
        filter(**params).values('channel'). \
        annotate(ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting")). \
        values('channel', 'ef_conf', 'in_conf')

    channal_list = bing_picture('channel', channal_dict, channal_set)

    # 部署咨询量饼状图
    deploy_list = []
    deploy_set = RefactoringConsultingAndVisitors.objects.all(). \
        filter(**params).values('deploy'). \
        annotate(ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting")). \
        values('deploy', 'ef_conf', 'in_conf')

    deploy_list = bing_picture('deploy', deploy_dict, deploy_set)

    # 部署咨询量折线图
    # 目标数据结构  [{"data":[23,3,4], "name": "标准版"}, {"data":[2,4,5,6], "name": 缺省}]
    dez_list = []
    for de in deploy_dict:
        dez_dict = {}
        # 遍历所有部署方式
        dep_zhe = de
        dez_set = RefactoringConsultingAndVisitors.objects.filter(**params).filter(deploy=dep_zhe).\
                  values('date').annotate(ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting")).\
                  values_list('date', 'ef_conf', 'in_conf')

        for it in dez_set:
            sum_it = int(it[1])+int(it[2])
            dez_dict.update({it[0]: sum_it})

        # 补齐没有咨询量的日期的数据
        que_date = patch_zero(from_date, to_date, dez_dict)
        dez_list.append({'name': deploy_dict[de], 'data': que_date.values()})

    gride_list = []
    # 以节点为维度，取有效咨询量和无效咨询量之和排名前十的数据
    grid_set = RefactoringConsultingAndVisitors.objects.all(). \
                   filter(**params).values('grid'). \
                   annotate(ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting")). \
                   order_by(F('ef_conf') + F('in_conf')).reverse()[:10]. \
        values('grid', 'ef_conf', 'in_conf')

    for grid in grid_set:
        ef_conf = grid.get("ef_conf", 0)
        in_conf = grid.get("in_conf", 0)
        grid["total"] = int(ef_conf) + int(in_conf)

        del grid["ef_conf"]
        del grid["in_conf"]

        if int(grid["total"]) != 0:
            grid["percent"] = round((int(grid["total"]) / total_con) * 100, 3)
        else:
            grid["percent"] = 0
        gride_list.append(grid)

    # 行业咨询量top10
    industry_list = []
    industry_dict = {}
    # 以行业为维度，取有效咨询量和无效咨询量之和排名前十的数据
    industry_set = RefactoringConsultingAndVisitors.objects.all(). \
                       filter(**params).values('industry'). \
                       annotate(ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting")). \
                       order_by(F('ef_conf') + F('in_conf')).reverse()[:10]

    industry_dict["data"] = []
    industry_dict["industry"] = []

    for industry in industry_set:
        ef_conf = industry.get("ef_conf", 0)
        in_conf = industry.get("in_conf", 0)
        con = int(ef_conf) + int(in_conf)
        per = round((con / total_con) * 100, 2)
        percent = str(per) + '%'
        industry_dict["data"].append({"value": con, "per": percent})
        industry_dict["industry"].append(industry["industry"])
        industry_dict["name"] = "咨询量"

    industry_list.append(industry_dict)

    data = {"con": conz_list, "vis": visz_list, "channal": channal_list,
            "grid": gride_list, "deploy": deploy_list, "dez": dez_list, "industry": industry_list}
    return Response(data=data, status=status.HTTP_200_OK)


# 企业数据统计
@api_view(['GET'])
@permission_classes([CompanyDataPermission, ])
def company_data(request):
    # 开始日期
    from_date = str_to_date(request.GET.get("from_date", "").strip())
    # 结束日期
    to_date = str_to_date(request.GET.get("to_date", "").strip())
    # 企业id
    company_id = request.GET.get("company_id", "").strip()
    # 是否有对比上周条件
    compare = request.GET.get("compare", "").strip()

    data = {}
    params = {}
    params_compare = {}
    week = datetime.timedelta(days=7)

    if from_date and to_date:
        params["date__gte"] = from_date
        params["date__lte"] = to_date

    queryset = RefactoringConsultingAndVisitors.objects.filter(**params).all()
    site_company = get_site_company()
    data["company_name"] = ""

    # 构造对比时间段
    compare_from = from_date - week
    compare_to = to_date - week
    params_compare["date__gte"] = compare_from
    params_compare["date__lte"] = compare_to
    queryset_compare = RefactoringConsultingAndVisitors.objects.filter(**params_compare).all()

    if company_id != "":
        # 判断该企业
        exists =RefactoringConsultingAndVisitors.objects.filter(company_id=company_id).exists()
        if exists:
            queryset = queryset.filter(company_id=company_id)
        else:
            return Response(data={"error": "该企业不存在"}, status=status.HTTP_400_BAD_REQUEST)

        if compare == '1':
            queryset_compare = queryset_compare.filter(company_id=company_id)
        # 获取企业名称
        for site in site_company:
            if company_id == site["siteid"]:
                data["company_name"] = site["name"]
                break
    # 咨询量
    conz_list = []
    # 访客量
    visz_list = []

    result_set = queryset.values('date').\
               annotate(ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting"),
                        ef_vis=Sum('unique_vistor')). \
               values_list('date', 'ef_conf', 'in_conf', 'ef_vis')

    # 初步获取咨询量和访客量
    conz_dict, visz_dict = initial_dict(result_set)
    # 补0数据
    conz_date = patch_zero(from_date, to_date, conz_dict)
    conz_list.append({'name': "咨询量", 'data': conz_date.values()})

    # 补齐没有访客量的日期的数据
    visz_date = patch_zero(from_date, to_date, visz_dict)
    visz_list.append({'name': "访客量", 'data': visz_date.values()})

    # 对比条件咨询量&访客量
    if compare == '1':
        compare_set = queryset_compare.values('date'). \
                      annotate(ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting"),
                      ef_vis=Sum('valid_visitors')). \
                      values_list('date', 'ef_conf', 'in_conf', 'ef_vis')
        # 初步获取咨询量和访客量
        conz_compare, visz_compare = initial_dict(compare_set)
        conz_compare = patch_zero(compare_from, compare_to, conz_compare)
        conz_list.append({'name': "对比上周咨询量", 'data': conz_compare.values()})
        visz_compare = patch_zero(compare_from, compare_to, visz_compare)
        visz_list.append({'name': "对比上周访客量", 'data': visz_compare.values()})

    data.update({"con": conz_list, "vis": visz_list})
    OperateLog.create_log(request)
    return Response(data=data, status=status.HTTP_200_OK)


# 初步获取咨询量，访客量数据折线图
def initial_dict(args):
    conz_dict = {}
    visz_dict = {}

    for result in args:
        if len(result) == 4:
            r0, r1, r2, r3 = result[0], result[1], result[2], result[3]
            sum_conz = int(r1) + int(r2)
            sum_visz = int(r3)
            conz_dict.update({r0: sum_conz})
            visz_dict.update({r0: sum_visz})
        elif len(result) == 2:
            r0, r1 = result[0], result[1]
            sum_conz = int(r1)
            conz_dict.update({r0: sum_conz})
            visz_dict.update({r0: sum_conz})

    return conz_dict, visz_dict


# 对没有数据的用0补位
def patch_zero(from_date, to_date, kwargs):
    dict_0 = {}
    for day in dates_during(from_date, to_date):
        if day not in kwargs.keys():
            dict_0.update({day: 0})
        else:
            dict_0.update({day: kwargs[day]})
    return dict_0


# 饼状图数据处理
def bing_picture(name, name_dict, queryset):
    l=[]
    for channal in queryset:
        ef_conf = channal.get("ef_conf", 0)
        in_conf = channal.get("in_conf", 0)
        channal["value"] = int(ef_conf) + int(in_conf)
        ch = channal[name]
        d_name = name_dict[ch]
        channal["name"] = d_name
        del channal["ef_conf"]
        if in_conf != 0:
            del channal["in_conf"]
        del channal[name]
        l.append(channal)
    return l


# 获取今天总得咨询量，昨天的总咨询量
def today_yesterday_num(ty_set):
    # 有效数据
    valid = ty_set.get("valid")
    # 无效数据
    unvalid = ty_set.get("unvalid")
    if valid == None:
        valid = 0
    if unvalid == None:
        unvalid = 0
    result = valid + unvalid
    return result


# 获取percent和rate
def get_percent(today, yesterday):
    # 如果今天和昨天都不为0
    if today != 0 and yesterday != 0:
        per = today / yesterday
        p = round((per -1) * 100, 3)
    # 如果今天不为0，昨天为0
    elif today != 0 and yesterday == 0:
        p = 100
    elif (today == 0 and yesterday != 0) or (today == 0 and yesterday == 0):
        p = 0

    # 获取rate的值
    if p > 0:
        rate = 1
    elif p == 0:
        rate = 0
    elif p < 0:
        rate = -1

    # 对负号处理
    if str(p).startswith('-'):
        p = str(p)[1:-1]
    else:
        p = p
    return p, rate


# 经典版数据
# 企业数据统计
@api_view(['GET'])
@permission_classes([CompanyDataPermission, ])
def jd_company_data(request):
    # 开始日期
    from_date = str_to_date(request.GET.get("from_date", "").strip())
    # 结束日期
    to_date = str_to_date(request.GET.get("to_date", "").strip())
    # 企业id
    company_id = request.GET.get("company_id", "").strip()
    # 是否有对比上周条件
    compare = request.GET.get("compare", "").strip()

    data = {}
    params = {}
    params_compare = {}
    week = datetime.timedelta(days=7)

    if from_date and to_date:
        params["date__gte"] = from_date
        params["date__lte"] = to_date

    # 构造对比时间段
    compare_from = from_date - week
    compare_to = to_date - week
    params_compare["date__gte"] = compare_from
    params_compare["date__lte"] = compare_to

    # 无对比条件咨询量&访客量查询集
    query_inquire = InquiriesData.objects.filter(**params).all()
    query_visitor = VistorData.objects.filter(**params).all()
    # 有对比条件的咨询量&访客量查询集
    comapre_inquire = InquiriesData.objects.filter(**params_compare).all()
    comapre_visitor = VistorData.objects.filter(**params_compare).all()

    data["company_name"] = ""

    # 判断该企业id
    if company_id != "":
        query_inquire = query_inquire.filter(company_id=company_id)
        query_visitor = query_visitor.filter(company_id=company_id)

        if compare == '1':
            comapre_inquire = comapre_inquire.filter(company_id=company_id)
            comapre_visitor = comapre_visitor.filter(company_id=company_id)
        # 获取企业名称
        try:
            company_name = OpenStationManage.objects.filter(station_info__company_id=company_id).\
                           first().company_info.company_name
            data["company_name"] = company_name
        except:
            pass

    # 咨询量
    conz_list = []
    # 访客量
    visz_list = []

    inquire_set = query_inquire.values('date').annotate(ef_conf=Sum('inquires_num')).values_list('date', 'ef_conf')
    visitor_set = query_visitor.values('date').annotate(ef_conf=Sum('visitor_num')).values_list('date', 'ef_conf')

    # 初步获取咨询量
    conz_dict, _ = initial_dict(inquire_set)

    visz_dict, _ = initial_dict(visitor_set)

    # 补0数据
    conz_date = patch_zero(from_date, to_date, conz_dict)
    conz_list.append({'name': "咨询量", 'data': conz_date.values()})

    # 补齐没有访客量的日期的数据
    visz_date = patch_zero(from_date, to_date, visz_dict)
    visz_list.append({'name': "访客量", 'data': visz_date.values()})

    # 对比条件咨询量&访客量
    if compare == '1':
        compare_inquire = comapre_inquire.values('date').annotate(ef_conf=Sum('inquires_num')).values_list('date', 'ef_conf')
        comapre_visitor = comapre_visitor.values('date').annotate(ef_conf=Sum('visitor_num')).values_list('date', 'ef_conf')

        # 初步获取咨询量和访客量
        conz_compare, _ = initial_dict(compare_inquire)
        visz_compare, _ = initial_dict(comapre_visitor)
        conz_compare = patch_zero(compare_from, compare_to, conz_compare)
        conz_list.append({'name': "对比上周咨询量", 'data': conz_compare.values()})
        visz_compare = patch_zero(compare_from, compare_to, visz_compare)
        visz_list.append({'name': "对比上周访客量", 'data': visz_compare.values()})

    data.update({"con": conz_list, "vis": visz_list})

    return Response(data=data, status=status.HTTP_200_OK)


# 首页上面4个数据块展示
@api_view(['GET'])
@permission_classes([DataOverviewPermission, ])
def jd_home_top(request):
    op_jd = OpenStationManage.objects.filter(station_info__classify=1).count()

    data = []
    # 咨询量基础查询集
    total_inquire_query = InquiriesData.objects.values('inquires_num')
    # 历史咨询总量
    history_inquire = total_inquire_query.aggregate(total=Sum('inquires_num'))

    i_dict = {"name": "经典版历史咨询量", "total": history_inquire["total"]}
    data.append(i_dict)

    # 访客量基础查询集
    total_visitor_qurey = VistorData.objects.all().values('visitor_num')
    history_vistor = total_visitor_qurey.aggregate(total=Sum('visitor_num'))
    v_dict = {"name": "经典版历史访客量", "total": history_vistor["total"]}
    data.append(v_dict)

    # 站点数量
    s_dict = {"name": "经典版历史站点数量", "total": op_jd}
    data.append(s_dict)

    return Response(data=data, status=status.HTTP_200_OK)


# 首页其余数据展示
@api_view(['GET'])
@permission_classes([DataOverviewPermission, ])
def jd_home_rest(request):

    params = dict()

    from_date = str_to_date(request.GET.get("from_date", "").strip())
    to_date = str_to_date(request.GET.get("to_date", "").strip())

    if from_date and to_date:
        params["date__gte"] = from_date
        params["date__lte"] = to_date

    # 该时间段内的总的咨询量
    all_con = InquiriesData.objects.all().filter(**params).values('inquires_num')
    all_set = all_con.aggregate(valid=Sum('inquires_num'))
    total_con = all_set.get("valid", 0)
    if total_con == None:
        total_con = 0
    total_con = int(total_con)

    # 咨询量和访客量数据
    conz_list = []
    visz_list = []

    # 咨询量
    inquire_query = InquiriesData.objects.filter(**params).values('date').\
                    annotate(value=Sum('inquires_num')).values_list('date', 'value')
    conz_dict, _ = initial_dict(inquire_query)
    # 补0数据
    conz_date = patch_zero(from_date, to_date, conz_dict)
    conz_list.append({'name': "咨询量", 'data': conz_date.values()})

    # 访客量
    visitor_query = VistorData.objects.filter(**params).values('date').\
                    annotate(value=Sum('visitor_num')).values_list('date','value')
    vis_dict, _ = initial_dict(visitor_query)
    # 补齐没有访客量的日期的数据
    visz_date = patch_zero(from_date, to_date, vis_dict)
    visz_list.append({'name': "访客量", 'data': visz_date.values()})

    # 咨询量渠道占比

    channal_set = InquiriesData.objects.all(). \
        filter(**params).values('channel'). \
        annotate(ef_conf=Sum('inquires_num')). \
        values('channel', 'ef_conf')
    channal_list = bing_picture('channel', jdchannal_dict, channal_set)

    # 部署咨询量饼状图
    deploy_list = []
    deploy_set = InquiriesData.objects.all(). \
        filter(**params).values('deploy_way'). \
        annotate(ef_conf=Sum('inquires_num')). \
        values('deploy_way', 'ef_conf')

    deploy_list = bing_picture('deploy_way', deploy_dict, deploy_set)

    # 部署咨询量折线图
    # 目标数据结构  [{"data":[23,3,4], "name": "标准版"}, {"data":[2,4,5,6], "name": 缺省}]
    dez_list = []
    for de in deploy_dict:
        dez_dict = {}
        # 遍历所有部署方式
        dep_zhe = de
        dez_set = InquiriesData.objects.filter(**params).filter(deploy_way=dep_zhe).\
                  values('date').annotate(ef_conf=Sum('inquires_num')).\
                  values_list('date', 'ef_conf')
        dez_dict, _ = initial_dict(dez_set)
        # 补齐没有咨询量的日期的数据
        que_date = patch_zero(from_date, to_date, dez_dict)
        dez_list.append({'name': deploy_dict[de], 'data': que_date.values()})

    grid_list = []
    # 以节点为维度，取有效咨询量和无效咨询量之和排名前十的数据
    grid_set = InquiriesData.objects.all(). \
                   filter(**params).values('grid'). \
                   annotate(ef_conf=Sum('inquires_num')). \
                   order_by('ef_conf').reverse()[:10]. \
        values('grid', 'ef_conf')

    for grid in grid_set:
        ef_conf = grid.get("ef_conf", 0)
        grid["total"] = int(ef_conf)

        del grid["ef_conf"]
        if total_con == 0:
            grid["percent"] = 0
        elif int(grid["total"]) != 0:
            grid["percent"] = round((int(grid["total"]) / total_con) * 100, 3)
        else:
            grid["percent"] = 0
        grid_list.append(grid)

    # 行业咨询量top10
    industry_list = []
    industry_dict = {}
    # 以行业为维度，效咨询量排名前十的数据
    industry_set = InquiriesData.objects.all(). \
                       filter(**params).values('industry'). \
                       annotate(ef_conf=Sum('inquires_num')). \
                       order_by('ef_conf').reverse()[:10]

    industry_dict["data"] = []
    industry_dict["industry"] = []

    for industry in industry_set:
        ef_conf = industry.get("ef_conf", 0)
        con = int(ef_conf)
        per = round((con / total_con) * 100, 2)
        percent = str(per) + '%'
        industry_dict["data"].append({"value": con, "per": percent})
        industry_dict["industry"].append(industry["industry"])
        industry_dict["name"] = "咨询量"

    industry_list.append(industry_dict)

    data = {"con": conz_list, "vis": visz_list, "channal": channal_list,
            "grid": grid_list, "deploy": deploy_list, "dez": dez_list, "industry": industry_list}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([GridDataPermission, ])
def get_grid_data(request):
    """
    暂时没用
    :param request:
    :return:
    """
    # 节点
    grid = request.GET.getlist('grid', '')

    if isinstance(grid, list) and len(grid) > 6:
        return Response({'error': '选择节点数超过6个！！！'}, status=status.HTTP_400_BAD_REQUEST)
    # 约束日期
    start_date = str_to_date(request.GET.get('start_date'))
    end_date = str_to_date(request.GET.get('end_date'))
    if not (end_date and start_date):
        return Response({'error': '请输入开始时间和结束时间！！！'}, status=status.HTTP_400_BAD_REQUEST)
    # 部署方式
    deploy = request.GET.get('deploy', '')
    # 默认是咨询量(0)  访客量是1
    index = request.GET.get('index', 0)

    params = {}
    params["date__gte"] = start_date
    params["date__lte"] = end_date

    # 基础查询集
    base_query = RefactoringConsultingAndVisitors.objects.all().filter(**params)

    # 如果存在部署方式
    if deploy:
        base_query = base_query.filter(deploy=deploy)

    consult = base_query.aggregate(invalid=Sum('valid_consulting'), valid=Sum('invalid_consulting'))
    invalid = consult.get("invalid")
    valid =consult.get("valid")
    if invalid == None:
        invalid = 0
    if valid == None:
        valid = 0
    consult_num = valid + invalid

    visitors = base_query.aggregate(total=Sum('unique_vistor'))
    visitor = visitors.get("total")
    if visitor == None:
        visitor = 0
    visitor_num = visitor

    # 有节点参数
    if grid:
        inq_list = []
        vis_list = []
        for g in grid:
            inquire_set = base_query.filter(grid=g).values('date').annotate(
                        ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting"),
                        ef_vis=Sum('unique_vistor')). \
                        values_list('date', 'ef_conf', 'in_conf', 'ef_vis')

            # 初始化咨询量&访客量
            inq_dict, vis_dict = initial_dict(inquire_set)

            # 补齐没有咨询量&访客的日期的数据
            que_date = patch_zero(start_date, end_date, inq_dict)
            vis_date = patch_zero(start_date, end_date, vis_dict)
            inq_list.append({"name": g, 'data': que_date.values()})
            vis_list.append({"name": g, 'data': vis_date.values()})
    else:
        inq_list = []
        vis_list = []
        inquire_set = base_query.values('date').annotate(
            ef_conf=Sum('valid_consulting'), in_conf=Sum("invalid_consulting"),
            ef_vis=Sum('unique_vistor')). \
            values_list('date', 'ef_conf', 'in_conf', 'ef_vis')
        # 初始化咨询量&访客量
        inq_dict, vis_dict = initial_dict(inquire_set)
        # 补齐没有咨询量&访客的日期的数据
        que_date = patch_zero(start_date, end_date, inq_dict)
        vis_date = patch_zero(start_date, end_date, vis_dict)
        inq_list.append({"name": "all", 'data': que_date.values()})
        vis_list.append({"name": "all", 'data': vis_date.values()})

    # 显示访客量
    if index == '1':
        broken_line = vis_list
    # 显示咨询量
    else:
        broken_line = inq_list

    grid_set = RefactoringConsultingAndVisitors.objects.filter(**params).values_list('grid', flat=True)
    grid_list = list(set(grid_set))
    deploy_list = []
    deploy_dict = dict(DEPLOY_WAYS)
    for key, value in deploy_dict.items():
        deploy_list.append({'name': value, 'value': key})

    data_dict = {
        "consult": consult_num,
        "visitors": visitor_num,
        "broken_line": broken_line,
        "deploy_list": deploy_list,
        "grid_list": grid_list,
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


# 经典版节点统计数据
# 节点统计数据
@api_view(['GET'])
@permission_classes([GridDataPermission, ])
def jd_grid_data(request):
    # 节点
    grid = request.GET.getlist('grid', '')

    if isinstance(grid, list) and len(grid) > 6:
        return Response({'error': '选择节点数超过6个！！！'}, status=status.HTTP_400_BAD_REQUEST)
    # 约束日期
    start_date = str_to_date(request.GET.get('start_date'))
    end_date = str_to_date(request.GET.get('end_date'))
    if not (end_date and start_date):
        return Response({'error': '请输入开始时间和结束时间！！！'}, status=status.HTTP_400_BAD_REQUEST)
    # 部署方式
    deploy = request.GET.get('deploy', '')
    # 默认是咨询量(0)  访客量是1
    index = request.GET.get('index', 0)

    params = {}
    params["date__gte"] = start_date
    params["date__lte"] = end_date

    # 咨询量基础查询集
    base_inquire = InquiriesData.objects.filter(**params)
    # 访客量基础查询集
    base_visitor = VistorData.objects.all().filter(**params)

    # 如果存在部署方式
    if deploy:
        base_inquire = base_inquire.filter(deploy_way=deploy)
        base_visitor = base_visitor.filter(deploy_way=deploy)

    # 有节点参数
    if grid:
        inq_list = []
        vis_list = []
        consult = base_inquire.filter(grid__in=grid).aggregate(total=Sum('inquires_num'))
        visitors = base_visitor.filter(grid__in=grid).aggregate(total=Sum('visitor_num'))
        for g in grid:
            inquire_set = base_inquire.filter(grid=g).values('date').\
                           annotate(ef_conf=Sum('inquires_num')).\
                           values_list('date', 'ef_conf')
            visitor_st = base_visitor.filter(grid=g).values('date').\
                           annotate(ef_conf=Sum('visitor_num')).\
                           values_list('date', 'ef_conf')

            # 初始化咨询量&访客量
            inq_dict, _ = initial_dict(inquire_set)
            vis_dict, _ = initial_dict(visitor_st)
            # 补齐没有咨询量&访客的日期的数据
            que_date = patch_zero(start_date, end_date, inq_dict)
            vis_date = patch_zero(start_date, end_date, vis_dict)
            inq_list.append({"name": g, 'data': que_date.values()})
            vis_list.append({"name": g, 'data': vis_date.values()})
    else:
        consult = base_inquire.aggregate(total=Sum('inquires_num'))
        visitors = base_visitor.aggregate(total=Sum('visitor_num'))
        inq_list = []
        vis_list = []
        inquire_set = base_inquire.values('date').\
                           annotate(ef_conf=Sum('inquires_num')).\
                           values_list('date', 'ef_conf')
        visitor_st = base_visitor.values('date'). \
                        annotate(ef_conf=Sum('visitor_num')). \
                        values_list('date', 'ef_conf')
        # 初始化咨询量&访客量
        inq_dict, _ = initial_dict(inquire_set)
        vis_dict, _ = initial_dict(visitor_st)
        # 补齐没有咨询量&访客的日期的数据
        que_date = patch_zero(start_date, end_date, inq_dict)
        vis_date = patch_zero(start_date, end_date, vis_dict)
        inq_list.append({"name": "all", 'data': que_date.values()})
        vis_list.append({"name": "all", 'data': vis_date.values()})

    # 显示访客量
    if index == '1':
        grid_set = VistorData.objects.filter(**params).values_list('grid', flat=True)
        broken_line = vis_list
    # 显示咨询量
    else:
        grid_set = InquiriesData.objects.filter(**params).values_list('grid', flat=True)
        broken_line = inq_list

    grid_list = list(set(grid_set))
    deploy_list = []
    deploy_dict = dict(DEPLOY_WAYS)
    for key, value in deploy_dict.items():
        deploy_list.append({'name': value, 'value': key})

    data_dict = {
        "consult": consult["total"],
        "visitors": visitors["total"],
        "broken_line": broken_line,
        "deploy_list": deploy_list,
        "grid_list": grid_list,
    }
    return Response(data=data_dict, status=status.HTTP_200_OK)


# 经典版节点表格数据
@api_view(['GET'])
@permission_classes([GridDataPermission, ])
def jd_grid_form(request):
    today = datetime.date.today()
    # 排序方式
    rules = request.GET.get("rules", )
    # 页码
    page = request.GET.get('page', 1)

    # 节点参数
    grid_name = request.GET.getlist('grid', '')

    if grid_name:
        re_data_front = InquiriesData.objects.all().filter(grid__in=grid_name).filter(date=today) \
            .values('company_id').annotate(con=Sum('inquires_num')) \
            .values('company_id', 'con', 'grid')

        # 升序
        if rules == '0':
            re_data = re_data_front.order_by('con')
        # 降序
        else:
            re_data = re_data_front.order_by('con').reverse()

        total_count_number = 0
        re_list = []
        index = 0
        for item in re_data:
            company_id = item.get('company_id')
            # company_info = OpenStationManage.objects.all().filter(station_info__company_id=company_id)\
            #     .select_related('company_info__company_name').values('company_info__company_name')
            value = int(item.get('con'))
            grid = item.get('grid')
            total_count_number += value
            index += 1
            re_list.append({'company_id': company_id, 'grid': grid, 'value': value, 'index': index})

        for i in re_list:
            value = i.get('value')
            if value:
                i['proportion'] = round((value / total_count_number) * 100, 6)
            else:
                i['proportion'] = 0
        # 总页数
        i, f = str(len(re_list) / 10).split('.')
        total_page = int(i) + 1 if not f else int(i)
        total_page = total_page if total_page else 1
        total_page = total_page if len(re_list) else 0

        total_count = int(page)
        front = (total_count - 1) * 10
        back = total_count * 10

        # 最后一页
        if total_count == total_page:
            data = re_list[front:]
            return Response(data={"total_page": total_page, "total_count": len(re_list), "data": data},
                            status=status.HTTP_200_OK)
        data = re_list[front:back]

        return Response(data={"total_page": total_page, "total_count": len(re_list), "data": data},
                        status=status.HTTP_200_OK)

    if page == 1:
        start = 0
        end = 10
    else:
        start = 10 * (int(page) - 1)
        end = 10 * int(page)

    today = datetime.date.today()
    # 基础查询集
    base_set = InquiriesData.objects.filter(date=today).\
                 values('grid', 'inquires_num')
    # 今天咨询量总和
    sum_inquire = base_set.aggregate(total=Sum('inquires_num')).get("total")

    # 升序
    if rules == '0':
        grid_set = base_set.values('grid').annotate(value=Sum('inquires_num')).\
                     values('grid', 'value').order_by('value')
    # 降序
    else:
        grid_set = base_set.values('grid').annotate(value=Sum('inquires_num')). \
                    values('grid', 'value').order_by('value').reverse()

    total_count = len(grid_set)

    # 获取总页数
    total_page = total_count // 10
    total_page = total_page + 1

    index = start +1
    data = []
    for grid in grid_set[start:end]:
        value = grid.get("value", 0)
        if sum_inquire == 0:
            grid["proportion"] = 0
        elif value == 0:
            grid["proportion"] = 0
        else:
            grid["proportion"] = round((value / sum_inquire) * 100, 6)
        grid["index"] = index
        index += 1
        data.append(grid)
    return Response(data={"total_page": total_page, "total_count": total_count, "data": data}, status=status.HTTP_200_OK)


# 经典版节点(经典版增加节点数据)
def add_grid():
    date = str_to_date("2018-08-01")
    inquir = InquiriesData.objects.filter(date__gte=date).all()
    for i in inquir:
        group_name = i.server_grp
        try:
            grid = Grid.objects.get(group__group_name=group_name).grid_name
        except:
            grid = 0
        i.grid = grid
        i.save()


# 删除有问题的咨询量
def del_inquires():
    inq = VistorData.objects.filter(date__in=(str_to_date('2018-09-11'),str_to_date('2018-09-12'))).delete()