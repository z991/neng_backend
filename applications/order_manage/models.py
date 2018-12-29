# Create your models here.
import time
from django.db import models
from common.models import SoftDeleteModel, TimeStampModel
from datetime import datetime
from django.contrib.auth.models import User
from applications.goods.models import SingleGoods, MultipleGoods
from ldap_server.configs import ORDER_STATUS, GOODS_TYPE
from ldap_server.configs import STATION_CHOICES, CUSTOM_TYPES, DEPLOY_WAYS, CLI_CHOICES, CUSTOM_NEW, PROD_SERV_VERSIONS
from applications.workorder_manage.models import OpenStationManage


time_date = time.strftime("%Y-%m-%d %H:%M:%S")


class OrderGoods(models.Model):
    """
    订单产品信息
    """
    order = models.ForeignKey('OrderInfo', null=True, related_name='order_cp', verbose_name='订单信息')
    s_order_goods = models.ForeignKey('goods.SingleGoods', null=True, blank=True, related_name='s_orders_goods',
                                      verbose_name='订单中单品')
    m_order_goods = models.ForeignKey('goods.MultipleGoods', null=True, blank=True, related_name='m_orders_goods',
                                      verbose_name='订单中组合商品')
    goods_num = models.IntegerField(verbose_name='购买数量', null=True, blank=True)

    class Meta:
        permissions = (
            ("view_ordergoods", "Can see available order goods"),
        )
        verbose_name = u"订单产品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.s_order_goods, self.m_order_goods)


class OrderInfo(models.Model):
    """
    订单信息
    """
    order_sn = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name="订单号")
    order_year = models.IntegerField(default=1, verbose_name='购买年限')
    give_day = models.IntegerField(default=0,verbose_name='赠送天数')

    order_statu = models.IntegerField(choices=ORDER_STATUS, default=1, verbose_name="订单状态")
    order_mount = models.FloatField(default=0.0, verbose_name="订单金额")
    order_discount = models.IntegerField(default=100, verbose_name='折扣')
    username = models.ForeignKey('auth.User', null=True, blank=True, verbose_name="用户", on_delete=models.CASCADE,
                                 related_name='order_of')
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    open_order = models.OneToOneField('workorder_manage.OpenStationManage', related_name='order_info',
                                      on_delete=models.CASCADE, null=True)

    class Meta:
        permissions = (
            ("view_orderinfo", "Can see available order info"),
        )
        verbose_name = u"订单信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.order_sn)


class OrderStatus(models.Model):
    """
    订单状态
    """
    order_status = models.IntegerField(choices=ORDER_STATUS, verbose_name="订单状态")
    order_snz = models.ForeignKey('OrderInfo', null=True, related_name='order_zt', verbose_name='订单交易')
    order_date = models.DateTimeField(default=datetime.now,verbose_name='修改时间')
    order_operator = models.CharField(max_length=32, verbose_name='操作人')
    responsible_person = models.CharField(max_length=32, verbose_name='经办人')

    class Meta:
        permissions = (
            ("view_orderstatus", "Can see available order status"),
        )
        verbose_name = u"订单状态"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_status


class ShoppingCat(models.Model):
    """购物车"""
    goods = models.ForeignKey('goods.SingleGoods', related_name='shopping_cat', blank=True, null=True,
                              db_constraint=False, verbose_name='已加入购物车单品')
    m_goods = models.ForeignKey('goods.MultipleGoods', related_name='shopping_cat', blank=True, null=True,
                                db_constraint=False, verbose_name='已加入购物车的行业解决方案')
    goods_number = models.IntegerField(verbose_name='商品数量', default=1)
    user = models.ForeignKey('auth.User', verbose_name="用户", blank=True, null=True)

    class Meta:
        verbose_name_plural = verbose_name = '购物车'
        db_table = 'trades_shoppingcat'

    def __str__(self):
        return "%s 的购物车" % self.user.last_name
