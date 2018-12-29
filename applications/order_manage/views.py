import time
import json

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes

from applications.workorder_manage.models import AreaInfo
from .models import OrderInfo, OrderStatus
from .serializers import DetailOrderInfoSerializer
from applications.goods.models import MultipleGoods
from applications.setup.permissions import OrderGroupPermission
from applications.log_manage.models import OperateLog
# Create your views here.


class OaOrderListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    oa运营平台订单列表和订单详情
    """
    serializer_class = DetailOrderInfoSerializer
    permission_classes = [OrderGroupPermission, ]
    # pagination_class = None

    def get_queryset(self):

        queryset = OrderInfo.objects.all().order_by('-id')

        order_sn = self.request.GET.get('order_sn', '').strip()
        order_status = self.request.GET.get('order_status', '').strip()
        company_name = self.request.GET.get('company_name', '').strip()
        sales = self.request.GET.get('sales', '').strip()

        if order_sn:
            queryset = queryset.filter(order_sn__icontains=order_sn)
        if order_status:
            queryset = queryset.filter(order_statu=order_status)
        if company_name:
            queryset = queryset.filter(open_order__company_info__company_name__icontains=company_name)
        if sales:
            queryset = queryset.filter(open_order__station_info__sales__icontains=sales)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        修改详情数据结构
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        dat = serializer.data
        provienc_num = dat['open_order']['company_info']['company_address']['province']
        city_num = dat['open_order']['company_info']['company_address']['city']
        station_type = dat['open_order']['company_info']['station_type']
        cli_version = dat['open_order']['station_info']['cli_version']
        customer_type = str(dat['open_order']['company_info']['customer_type'])

        station_dic = {1: '试用客户', 2: '正式客户', 3: '市场渠道客户', 4: '商务渠道客户', 5: '自用站点'}
        cli_dic = {1: 'B2B', 2: 'B2C', 3: '不限', 4: 'B2B2C'}
        customer = {'False': '新客户', 'True': '老客户'}

        dat['open_order']['company_info'].update({'station_type':station_dic[station_type]})
        dat['open_order']['station_info'].update({'cli_version':cli_dic[cli_version]})

        provienc= AreaInfo.objects.get(pk=provienc_num).atitle
        city = AreaInfo.objects.get(pk=city_num).atitle
        customer_type = customer[customer_type]

        dat['open_order']['company_info']['company_address'].update({'province':provienc,'city':city})
        dat['open_order']['station_info'].update({"deploy_way": '公有云'})
        dat['open_order']['company_info'].update({'customer_type': customer_type})
        for i in dat['order_cp']:

            if i.get('s_order_goods'):
                i.update({'goods_attribute': "单件商品",
                          'goods_name':i['s_order_goods']['goods_name'],
                          'model_name':i['s_order_goods']['goods_model']['model_name'],
                          'num': '1',
                          "put_price":i['s_order_goods']["put_price"]
                          })
                del i['s_order_goods']

            if i.get('m_order_goods'):
                igoods = i['m_order_goods']['id']
                m = MultipleGoods.objects.get(pk=igoods)
                num = m.s_goods.all().count()

                i.update({'num':num,
                          'goods_attribute': "组合商品",
                          'goods_name': i['m_order_goods']['m_goods_name'],
                          "put_price": i['m_order_goods']["put_price"]
                          })
                del i['m_order_goods']

        order_zt = dat.get('order_zt')[-1]
        order_status = order_zt.get('order_status')
        status_dict = {1: "财务审核", 2: "开站中", 3: "实施中", 4: "交易成功", 5: "已失效"}
        order_status = status_dict[order_status]
        dat.update({"order_status": order_status})
        return Response(dat)


@api_view(['PUT'])
@permission_classes([OrderGroupPermission, ])
def status_create(request):
    bod = request.body
    bod = str(bod, encoding="utf-8")
    bod = json.loads(bod)
    or_status = bod.get('order_status', 2)

    user = request.user
    order_status = int(or_status)
    or_statu = order_status - 1
    responsible_person = bod.get('responsible_person', '0')
    info_id = bod.get('info_id', None)

    sta = OrderStatus.objects.filter(order_snz=info_id)
    ls = []
    for i in sta:
        ls.append(i.order_status)

    if 5 in ls:
        return Response({'error': '订单已失效，无法修改'}, status=status.HTTP_400_BAD_REQUEST)
    elif 4 in ls:
        return Response({'error': '订单已完成，无法修改'}, status=status.HTTP_400_BAD_REQUEST)
    elif order_status in ls:
        return Response({'error': '该状态已存在'}, status=status.HTTP_400_BAD_REQUEST)
    elif or_statu not in ls and order_status != 5:
        return Response({'error': '请按订单状态变更流程修改状态'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        order_snz = OrderInfo.objects.get(pk=info_id)
        time_date1 = str(time.strftime("%Y-%m-%d %H:%M:%S"))
        status_info ={
            'order_status': order_status,
            'order_date': time_date1,
            'order_operator': user,
            'responsible_person': responsible_person,
            'order_snz': order_snz
        }
        OrderStatus.objects.create(**status_info)
        res = OrderInfo.objects.filter(pk=info_id).update(order_statu=order_status)
        OperateLog.create_log(request)
        return Response({'info': '状态更新成功'}, status=status.HTTP_200_OK)
