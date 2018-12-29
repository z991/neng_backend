from django.db import models

# Create your models here.
from ldap_server.configs import TAG_CLASS, PUT_AWAY, SELL_STATUS,\
    RECOMMENDATION, ADVERTISING_POSITION, FILL_CONTROL
from common.models import SoftDeleteModel, TimeStampModel
from applications.production_manage.models import SingleSelection, FunctionInfo
from django.contrib.auth import get_user_model

User = get_user_model()


class GoodsModel(models.Model):
    model_name = models.CharField(max_length=16, unique=True, null=False, verbose_name='商品模块')
    good_parents = models.ForeignKey("self", max_length=16, null=True, verbose_name="所属父类",
                                     blank=True, related_name="goodmodel")

    class Meta:
        permissions = (
            ("view_goodsmodel", "Can see available goods model"),
        )
        verbose_name_plural = verbose_name = "商品模块配置"

    def __str__(self):
        return self.model_name


# 详情页图片
class DetailImage(SoftDeleteModel, TimeStampModel):
    s_de_goods = models.ForeignKey('SingleGoods', related_name='detail_img', null=True, blank=True, default='',
                                   verbose_name="单品名称-detail")
    m_de_goods = models.ForeignKey('MultipleGoods', related_name='m_de_goods', null=True, blank=True, default='',
                                   verbose_name="组合商品名称-detail")
    image = models.URLField(default='', verbose_name="商品详情页", null=True, blank=True)
    weight = models.CharField(default=0, verbose_name="权重", null=True, blank=True, max_length=5)

    class Meta:
        verbose_name_plural = verbose_name = "详情页图片"

    def __str__(self):
        return '%s: %s' % (self.s_de_goods, self.m_de_goods)


class IntroduceImage(SoftDeleteModel, TimeStampModel):
    s_in_goods = models.ForeignKey('SingleGoods', null=True, related_name='introduce_img', blank=True, default='',
                                   verbose_name="单品名称-in")
    m_in_goods = models.ForeignKey('MultipleGoods', null=True, related_name='m_in_goods', blank=True, default='',
                                   verbose_name="组合商品名称-in")
    image = models.URLField(default='', verbose_name="产品介绍图片", null=True, blank=True)

    class Meta:
        verbose_name_plural = verbose_name = "产品介绍图片"

    def __str__(self):
        return '%s: %s' % (self.s_in_goods, self.m_in_goods)


class SuccessCaseImage(SoftDeleteModel, TimeStampModel):
    m_su_goods = models.ForeignKey('MultipleGoods', related_name='m_su_goods', null=True, blank=True, default='',
                                   verbose_name="组合商品名称-su")
    s_su_goods = models.ForeignKey('SingleGoods', related_name='success_img', null=True, blank=True, default='',
                                   verbose_name="单品名称-su")
    image = models.URLField(default='', verbose_name="成功案例图片", null=True, blank=True)

    class Meta:
        verbose_name_plural = verbose_name = "成功案例图片"

    def __str__(self):
        return '%s: %s' % (self.m_su_goods, self.s_su_goods)


class MultipleGoods(SoftDeleteModel, TimeStampModel):
    m_goods_sn = models.CharField(max_length=5,verbose_name='组合商品编码')
    m_goods_name = models.CharField(max_length=64,verbose_name='组合商品名称')
    m_goods_details_edit = models.TextField(verbose_name="详情页文案", default='')
    m_goods_brief_introduction = models.TextField(max_length=1000, verbose_name='产品简介')
    m_goods_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='商品价格')
    m_goods_attribute = models.CharField(max_length=16,default='组合商品',null=True,verbose_name='商品属性')

    m_goods_tag = models.ManyToManyField('TagClass',related_name='multiple_tag')
    s_goods = models.ManyToManyField('SingleGoods',related_name='multiple_member',blank=True,verbose_name='组合成员')

    putaway_recent_on_time = models.DateField(verbose_name="上架时间", null=True, blank=True, default='1970-01-01')
    # 下架时间
    putaway_off_time = models.DateField(verbose_name="下架时间", null=True, blank=True, default='1970-01-01')
    # 操作人
    putaway_operator = models.CharField(max_length=24, help_text='操作人', blank=True, null=True,default="putaway_operator")
    # 上架状态（上架，下架，待上架）
    sell_status = models.SmallIntegerField(choices=SELL_STATUS, default=1, null=False, help_text='售卖状态',
                                           verbose_name='售卖状态')
    recommend = models.SmallIntegerField(choices=RECOMMENDATION, default=2, verbose_name='是否首页展示')
    put_price = models.DecimalField(max_digits=11, decimal_places=2, default=1, verbose_name='组合上架价格', help_text='上架价格')

    class Meta:
        permissions = (
            ("view_multiplegoods", "Can see available multiplegoods"),
        )
        verbose_name_plural = verbose_name = "组合商品管理"

    def __str__(self):
        return self.m_goods_name


class TagClass(models.Model):
    label_category = models.SmallIntegerField(choices=TAG_CLASS, null=False, verbose_name='标签类别')
    goods_tag = models.CharField(max_length=16, null=False, verbose_name='商品标签')

    class Meta:
        # 联合字段唯一
        unique_together = ('label_category', 'goods_tag')
        permissions = (
            ("view_tagclass", "Can see available tagclass"),
        )
        verbose_name_plural = verbose_name = "标签模块配置"

    def __str__(self):
        return self.goods_tag


class Advertising(models.Model):
    ad_position = models.IntegerField(choices=ADVERTISING_POSITION, default=0, verbose_name='广告位置')
    ad_name = models.CharField(max_length=64, verbose_name='广告名称')
    ad_image = models.URLField(default='', verbose_name="广告轮播图")
    # 广告上架时间
    ad_put_recent_on = models.DateField(null=False, blank=False, verbose_name='广告最近上架时间')
    # 广告下架时间
    ad_put_off = models.DateField(null=False, blank=False, verbose_name='广告下架时间')
    # 广告上架操作人
    ad_put_operator = models.ForeignKey(User, blank=True, null=True, db_constraint=False,
                                        related_name='advertising', verbose_name='广告上架操作人')
    # 广告上架状态
    ad_status = models.IntegerField(choices=PUT_AWAY, default=3, null=False, verbose_name='广告上架状态')

    class Meta:
        permissions = (
            ("view_advertising", "Can see available advertising"),
        )
        verbose_name_plural = verbose_name = "广告管理"

    def __str__(self):
        return self.ad_name


class SingleGoods(SoftDeleteModel, TimeStampModel):
    goods_name = models.CharField(max_length=25, verbose_name='商品名称')
    goods_sn = models.CharField(max_length=5, verbose_name='商品编号', unique=True)
    goods_brief_introduction = models.TextField(max_length=100, verbose_name='产品简介')
    goods_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='商品价格')
    goods_text = models.TextField(verbose_name="详情页文案", default='')
    goods_attribute = models.CharField(max_length=16, default='单件商品', null=True, verbose_name='商品属性')

    parent = models.ForeignKey('SingleGoods', related_name='childfunc', blank=True, null=True, db_constraint=False,
                               verbose_name='前置产品')
    goods_tag = models.ManyToManyField('TagClass', related_name='single_goods', blank=True,
                                       verbose_name='商品标签')
    goods_selection = models.ManyToManyField(SingleSelection, related_name='single_goods', blank=True,
                                       verbose_name='功能开关选项值')
    goods_model = models.ForeignKey('GoodsModel', blank=True, max_length=16, related_name='good_model',
                                     null=True, verbose_name='所属模块')
    putaway_recent_on_time = models.DateField(verbose_name="上架时间", null=True, blank=True, default='1970-01-01')
    # 下架时间
    putaway_off_time = models.DateField(verbose_name="下架时间", null=True, blank=True, default='1970-01-01')
    # 操作人
    putaway_operator = models.CharField(max_length=24, help_text='操作人', blank=True, null=True, default="putaway_operator")
    sell_status = models.SmallIntegerField(choices=SELL_STATUS, default=1, null=False, help_text='售卖状态',
                                           verbose_name='售卖状态')
    recommend = models.SmallIntegerField(choices=RECOMMENDATION, default=2, verbose_name='是否首页展示')
    put_price = models.DecimalField(max_digits=9, decimal_places=2, default=0, verbose_name='上架价格')

    class Meta:
        permissions = (
            ("view_singlegoods", "Can see available singlegoods"),
        )
        verbose_name_plural = verbose_name = '单品管理'

    def __str__(self):
        return self.goods_name


class SpecificationParameter(SoftDeleteModel):
    """产品规格参数"""
    param_model = models.ForeignKey('GoodsModel', blank=True, related_name='param_model',
                                     null=True, verbose_name='所属模块')
    file_name = models.CharField(max_length=25, verbose_name='字段名称')
    fill_control = models.IntegerField(choices=FILL_CONTROL, default=1, verbose_name='填写控件类型')

    class Meta:
        verbose_name_plural = verbose_name = '产品规格和参数'

    def __str__(self):
        return self.file_name


class ParameterOptions(SoftDeleteModel):
    # 如果是单行文本框,名称和值就是相同的
    # 如果是单选框,选项值就只是对名称的解释没有实际意义
    control = models.ForeignKey(SpecificationParameter, related_name='param_control',
                                verbose_name='选项', db_constraint=False, null=True)
    param_options_name = models.CharField(max_length=100, default='Ture', verbose_name='控件选项名称')
    param_options_value = models.CharField(max_length=100, default='Ture', verbose_name='控件选项值')
    single_goods = models.ManyToManyField('SingleGoods', blank=True, related_name='par_options',
                                          verbose_name='单价产品')
    multiple_goods = models.ManyToManyField('MultipleGoods', blank=True, related_name='multiple_par_options',
                                            verbose_name='行业解决方案')

    class Meta:
        verbose_name_plural = verbose_name = '产品规格和参数选项'

    def __str__(self):
        return self.param_options_name
