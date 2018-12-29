import logging
import time
import requests
import json

from django.db import transaction
from applications.goods.models import GoodsModel, SingleGoods, MultipleGoods
from rest_framework import serializers
from .models import OrderInfo, OrderStatus, OrderGoods
from applications.workorder_manage.models import OpenStationManage, StationInfo


from applications.workorder_manage.serializers import CompanyInfoSerializer, OpenStationManageSerializer, StationInfoSerializer


class ViewModelSerializer(serializers.ModelSerializer):
    """
    购物车模块外键序列化器(订单中单品也适用)
    """
    class Meta:
        model = GoodsModel
        fields = ('id', 'model_name')


class OrderSingleSerializer(serializers.ModelSerializer):
    """
    订单单品相关序列化器
    """
    goods_model = ViewModelSerializer(read_only=True)

    class Meta:
        model = SingleGoods
        fields = ('id', 'goods_name','goods_model', 'put_price'
                  )


class OrderMuliteSerializer(serializers.ModelSerializer):
    """
    订单组合商品相关序列化器
    """
    class Meta:
        model = MultipleGoods
        fields = ('id', 'm_goods_name', 'put_price')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """
    订单商品序列化
    """
    s_order_goods = OrderSingleSerializer()
    m_order_goods = OrderMuliteSerializer()

    class Meta:
        model = OrderGoods
        fields = ('id', 's_order_goods', 'm_order_goods', 'goods_num')


class OrderStutasSerializer(serializers.ModelSerializer):
    """
    订单状态
    """
    order_date = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = OrderStatus
        fields = ('id', 'order_status', 'order_date', 'order_operator', 'responsible_person')


class StationSerializer(serializers.ModelSerializer):
    """
    站点信息
    """
    class Meta:
        model = StationInfo
        fields = ('id', 'deploy_way', 'validity_days', 'cli_version',
                  'sales', 'pre_sales', 'oper_cslt', 'impl_cslt', 'oper_supt')


class OpenSerializer(serializers.ModelSerializer):
    """
    开站信息序列化
    """
    #企业信息
    company_info = CompanyInfoSerializer(read_only=True)
    #站点信息
    station_info = StationInfoSerializer(read_only=True)

    class Meta:
        model = OpenStationManage
        fields = (
            'id', 'company_info', 'station_info')


class OrderInfoSerializer(serializers.ModelSerializer):
    """
    订单信息序列化(订单列表)
    """
    order_cp = OrderGoodsSerializer(many=True)
    order_zt = OrderStutasSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = ('id', 'order_sn', 'order_cp', 'order_zt', 'username', 'order_year', 'order_discount', 'order_mount')


class DetailOrderInfoSerializer(serializers.ModelSerializer):
    """
    订单详情信息序列化
    """
    order_cp = OrderGoodsSerializer(many=True)
    order_zt = OrderStutasSerializer(many=True)
    open_order = OpenSerializer()

    class Meta:
        model = OrderInfo
        fields = ('id', 'order_sn', 'order_cp', 'order_zt', 'username', 'order_year', 'order_discount', 'order_mount',
                  'open_order', 'give_day')


class SimOrderSingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleGoods
        fields = ('id', )


class SimOrderMulSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleGoods
        fields = ('id', )


class SimOrderGoodsSerializer(serializers.ModelSerializer):
    s_order_goods = SimOrderSingleSerializer(read_only=True)
    m_order_goods = SimOrderMulSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ('id', 's_order_goods', 'm_order_goods', 'goods_num')
