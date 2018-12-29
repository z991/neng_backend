import logging
import uuid
import time, datetime

from rest_framework import serializers
from django.db import transaction

from .models import GoodsModel, DetailImage, IntroduceImage, SuccessCaseImage
from applications.goods.models import SingleGoods, Advertising, TagClass, MultipleGoods,\
    SpecificationParameter, ParameterOptions
from applications.production_manage.models import SingleSelection, FunctionInfo
from django.contrib.auth import get_user_model

put_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
User = get_user_model()
log = logging.getLogger('django')


class ViewSelectionSerializer(serializers.ModelSerializer):
    """
    功能开关选项序列化(暂时没用上)
    """
    # def get_functions(self, selection):
    #     print(selection)
    #     ret = FunctionInfo.objects.all().filter(selection=selection)
    #     return ret
    #
    # functions = serializers.SerializerMethodField(read_only=True)

    # def to_native(self, value):
    #
    #     return 'hello'

    def to_representation(self, value):
        ret={}
        ret['id'] = value.id
        ret['select_name'] = value.select_name
        ret['select_value'] = value.select_value
        ret['function_name'] = value.function.func_name
        ret['function'] = value.function.id
        product = FunctionInfo.objects.all().filter(func_name=value.function).select_related('product')\
            .values_list('product__product', flat=True)
        ret['product'] = list(product)[0]
        return ret

    # def to_internal_value(self, data):
    #     print('*****2', data)

    # class Meta:
    #     model = SingleSelection
    #     fields = ('id', 'function', 'select_name', 'select_value')


class GoodsModelSerializer(serializers.ModelSerializer):
    '''
    商品所属模块
    '''
    class Meta:
        model = GoodsModel
        fields = ('id', 'model_name', 'good_parents')


class DetailImageSerializer(serializers.ModelSerializer):
    '''
    商品详情页图片
    '''
    class Meta:
        model = DetailImage
        fields = ('id', 'image', 'weight')


class IntroduceImageSerializer(serializers.ModelSerializer):
    '''
    商品介绍图片
    '''
    class Meta:
        model = IntroduceImage
        fields = ('id', 'image')


class SuccessCaseImageSerializer(serializers.ModelSerializer):
    '''
    商品成功案例图片
    '''
    class Meta:
        model = SuccessCaseImage
        fields = ('id', 'image')


class TagClassSerializer(serializers.ModelSerializer):
    '''
    商品标签
    '''
    class Meta:
        model = TagClass
        fields = ('id', 'label_category', 'goods_tag')


class TagClassBakSerializer(serializers.ModelSerializer):
    '''
    商品标签(复制)
    '''
    class Meta:
        model = TagClass
        fields = ('id', 'label_category', 'goods_tag')


class SimpSingleGoodsSerializer(serializers.ModelSerializer):
    # goods_model = serializers.SlugRelatedField(
    #     slug_field='model_name',
    #     read_only=False,
    #     many=True,
    #     queryset=GoodsModel.objects.all()
    # )
    goods_model = serializers.CharField(source='goods_model.model_name', read_only=True)

    class Meta:
        model = SingleGoods
        fields = ('id', 'goods_model', 'goods_name', 'goods_sn')


class ListAndGetSpecificationParameterSerializer(serializers.ModelSerializer):
    """
    GET and LIST 序列化
    """
    param_model = serializers.CharField(source='param_model.model_name', read_only=True)

    class Meta:
        model = SpecificationParameter
        fields = ('id', 'file_name', 'param_model', 'fill_control')


class ViewParameterOptionsSerializer(serializers.ModelSerializer):
    """
    产品规格参数选项序列化
    """
    class Meta:
        model = ParameterOptions
        fields = ('id', 'param_options_name', 'param_options_value')


class ViewSpecificationParameterSerializer(serializers.ModelSerializer):
    """
    产品规格参数序列化
    """
    param_control = ViewParameterOptionsSerializer(many=True, read_only=True)
    param_model = GoodsModelSerializer(read_only=True)

    class Meta:
        model = SpecificationParameter
        fields = ('id', 'file_name', 'fill_control', 'param_control', 'param_model')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                specification_info = super(ViewSpecificationParameterSerializer, self).create(validated_data)
                """
                {
                    "param_model": '',
                    "file_name": '',
                    "fill_control": '',
                    "param_control": [
                            {"param_options_name": ''},
                            {"param_options_name": ''}
                            ]
                }
                """
                # 所属模块
                param_model = self.initial_data['param_model']
                specification_info.param_model = GoodsModel.objects.get(pk=param_model)
                fill_control = self.initial_data['fill_control']
                # 如果是单行文本框(0)就是空列表, 如果是下拉列表框(1)就有name=value
                if fill_control == 1:
                    # 规格参数选项
                    options = self.initial_data['param_control']
                    opt_list = []
                    for opt in options:
                        opt_list.append(ParameterOptions(control=specification_info,
                                                         param_options_name=opt['param_options_name'],
                                                         param_options_value=opt['param_options_name']))
                    ParameterOptions.objects.bulk_create(opt_list)

                specification_info.save()
                return specification_info

        except Exception as e:
            log.error(e)
            raise TypeError(e)

    def update(self, instance, validated_data):
        instance = super(ViewSpecificationParameterSerializer, self).update(instance, validated_data)
        # 所属模块
        param_model = self.initial_data['param_model']
        instance.param_model = GoodsModel.objects.get(pk=param_model)
        # 选项
        fill_control = self.initial_data['fill_control']
        if fill_control == 1:
            options = self.initial_data['param_control']
            if instance.param_control:
                instance.param_control.clear()

            opt_list = []
            for opt in options:
                opt_list.append(ParameterOptions(
                    param_options_name=opt['param_options_name'],
                    param_options_value=opt['param_options_name'],
                    control=instance
                    ))
            ParameterOptions.objects.bulk_create(opt_list)

        instance.save()
        return instance


class SingleGoodsSerializer(serializers.ModelSerializer):
    # 商品标签
    goods_tag = TagClassSerializer(many=True, read_only=True)
    # 所属模块
    goods_model = GoodsModelSerializer(read_only=True)
    # 图片
    detail_img = DetailImageSerializer(many=True, read_only=True)
    introduce_img = IntroduceImageSerializer(many=True, read_only=True)
    success_img = SuccessCaseImageSerializer(many=True, read_only=True)
    # 功能开关选项
    goods_selection = ViewSelectionSerializer(many=True, read_only=True)
    # 规格参数
    par_options = ViewParameterOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = SingleGoods
        fields = (
            'id', 'goods_name', 'goods_sn', 'goods_brief_introduction', 'goods_price',
            'goods_text', 'goods_attribute', 'goods_model', 'parent', 'goods_tag',
            'detail_img', 'introduce_img', 'success_img', 'goods_selection', 'par_options')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                goods_info = super(SingleGoodsSerializer, self).create(validated_data)
                goods_info.goods_sn = 'A'+str(uuid.uuid4())[-4:]

                """
                产品规格参数
                """
                # parameter_id 这个键的值是一个列表
                parameter = self.initial_data['par_options']
                par_queryset = ParameterOptions.objects.all()
                for opt_id in parameter:
                    if (not isinstance(opt_id, int)) and (not isinstance(opt_id, dict)):
                        continue
                    # 如果是id则为下拉列表框,
                    if isinstance(opt_id, int):
                        options = par_queryset.get(pk=opt_id)
                        goods_info.par_options.add(options)
                    # 如果是字典则认为是单行文本框
                    if isinstance(opt_id, dict):
                        options_id = opt_id['id']
                        opts = SpecificationParameter.objects.get(pk=options_id)
                        options_value = opt_id['value']
                        ins_opt = ParameterOptions.objects.all().create(control=opts,
                                                                        param_options_name=options_value,
                                                                        param_options_value=options_value)
                        goods_info.par_options.add(ins_opt)
                """
                所属标签
                """
                # 根据id查询
                goods_tag_id = self.initial_data['goods_tag']
                tag_list = []
                tag_queryset = TagClass.objects.all()
                for good_tag_id in goods_tag_id:
                    good_tag = tag_queryset.get(pk=good_tag_id)
                    if good_tag:
                        tag_list.append(good_tag)
                goods_info.goods_tag = tag_list
                """
                所属模块
                """
                # 根据id查询
                goods_model_id = self.initial_data['goods_model']
                if GoodsModel.objects.all().filter(pk=goods_model_id):
                    goods_info.goods_model = GoodsModel.objects.all().get(pk=goods_model_id)
                '''
                前置产品
                '''
                # 新增产品时前置产品应该根据id查询已有的产品
                parent_id = self.initial_data['parent']
                if parent_id:
                    parent = SingleGoods.objects.all().get(pk=parent_id)
                    if parent:
                        goods_info.parent = parent
                '''
                产品图片
                '''
                # 图片在新增产品时根据图片信息创建
                s_imgs = self.initial_data['detail_img']
                img_list = []
                for detail_img in s_imgs:
                    img_list.append(DetailImage(s_de_goods=goods_info, image=detail_img['src']))
                DetailImage.objects.bulk_create(img_list)

                in_imgs = self.initial_data['introduce_img']
                in_img_list = []
                for introduce_img in in_imgs:
                    in_img_list.append(IntroduceImage(s_in_goods=goods_info, image=introduce_img['src']))
                IntroduceImage.objects.bulk_create(in_img_list)

                su_imgs = self.initial_data['success_img']
                su_img_list = []
                for success_img in su_imgs:
                    su_img_list.append(SuccessCaseImage(s_su_goods=goods_info, image=success_img['src']))
                SuccessCaseImage.objects.bulk_create(su_img_list)
                '''
                功能开关
                '''
                prod_func_list = self.initial_data['goods_selection']
                selc_queryset = SingleSelection.objects.all()
                for selc_id in prod_func_list:
                    goods_info.goods_selection.add(selc_queryset.get(pk=selc_id))
                goods_info.save()
                return goods_info

        except Exception as e:
            log.error(e)
            raise TypeError(e)

    def update(self, instance, validated_data):
        instance = super(SingleGoodsSerializer, self).update(instance, validated_data)

        """
        产品规格参数
        """
        # parameter_id 这个键的值是一个列表
        parameter = self.initial_data['par_options']
        instance.par_options.clear()
        par_queryset = ParameterOptions.objects.all()
        for opt_id in parameter:
            if (not isinstance(opt_id, int)) and (not isinstance(opt_id, dict)):
                continue
            # 如果是id则为下拉列表框,
            if isinstance(opt_id, int):
                options = par_queryset.get(pk=opt_id)
                if options:
                    instance.par_options.add(options)
            # 如果是字典则认为是单行文本框
            if isinstance(opt_id, dict):
                options_id = opt_id['id']
                opts = SpecificationParameter.objects.get(pk=options_id)
                options_value = opt_id['value']
                ins_opt = ParameterOptions.objects.all().create(control=opts,
                                                                param_options_name=options_value,
                                                                param_options_value=options_value)
                instance.par_option.add(ins_opt)
        """
        产品标签 断关系
        """
        instance.goods_tag.clear()
        goods_tag_list = self.initial_data['goods_tag']
        tag_list = []
        tag_query = TagClass.objects.all()
        for goods_tag_id in goods_tag_list:
            tag_list.append(tag_query.get(pk=goods_tag_id['id']))
            instance.goods_tag = tag_list
        """
        所属模块 断关系
        """
        goods_model_id = self.initial_data['goods_model']
        instance.goods_model = GoodsModel.objects.all().get(pk=goods_model_id)
        """
        前置产品 断关系
        """
        parent = self.initial_data['parent']
        if parent:
            instance.parent = SingleGoods.objects.all().get(pk=parent)
        """
        产品图片 删除
        """
        instance.detail_img.clear()
        detail_img_list = self.initial_data['detail_img']
        de_img_list = []
        for de_img in detail_img_list:
            de_img_list.append(DetailImage(s_de_goods=instance, image=de_img['image'], weight=de_img['weight']))
        DetailImage.objects.bulk_create(de_img_list)

        instance.introduce_img.clear()
        introduce_img_list = self.initial_data['introduce_img']
        in_img_list = []
        for in_img in introduce_img_list:
            in_img_list.append(IntroduceImage(s_in_goods=instance, image=in_img['image']))
        IntroduceImage.objects.bulk_create(in_img_list)

        instance.success_img.clear()
        success_img_list = self.initial_data['success_img']
        su_img_list = []
        for su_img in success_img_list:
            su_img_list.append(SuccessCaseImage(s_su_goods=instance, image=su_img['image']))
        SuccessCaseImage.objects.bulk_create(su_img_list)
        '''
        功能开关 断关系
        '''
        instance.goods_selection.clear()
        selc_id_list = self.initial_data['goods_selection']
        for func in selc_id_list:
            instance.goods_selection.add(SingleSelection.objects.all().get(pk=func['id']))
        instance.save()
        return instance


class SingleGoodsListSerializer(serializers.ModelSerializer):
    '''
    组合商品下拉单品接口
    '''
    class Meta:
        model = SingleGoods
        fields = ('id','goods_name',)


class SimpMultipleGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleGoods
        fields = ('id',  'm_goods_name', 'm_goods_sn')


class MultipleGoodsSerializer(serializers.ModelSerializer):
    '''
    组合商品
    '''
    m_de_goods = DetailImageSerializer(many=True, read_only=True)
    m_in_goods = IntroduceImageSerializer(many=True, read_only=True)
    m_su_goods = SuccessCaseImageSerializer(many=True, read_only=True)

    m_goods_tag = TagClassSerializer(many=True, read_only=True)
    s_goods = SimpSingleGoodsSerializer(many=True, read_only=True)
    # 规格参数
    multiple_par_options = ViewParameterOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = MultipleGoods
        fields = ('id', 'm_goods_sn', 'm_goods_name', 'm_goods_details_edit',
                  'm_goods_brief_introduction', 'multiple_par_options',
                  'm_goods_price', 'm_goods_attribute', 'm_goods_tag',
                  's_goods', 'm_de_goods', 'm_in_goods', 'm_su_goods',)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                m_goods_info = super(MultipleGoodsSerializer, self).create(validated_data)
                m_goods_info.m_goods_sn = 'B'+str(uuid.uuid4())[-4:]
                """
                产品规格参数
                """
                # parameter_id 这个键的值是一个列表
                parameter = self.initial_data['multiple_par_options']
                par_queryset = ParameterOptions.objects.all()
                for opt_id in parameter:
                    if (not isinstance(opt_id, int)) and (not isinstance(opt_id, dict)):
                        continue
                    # 如果是id则为下拉列表框,
                    if isinstance(opt_id, int):
                        options = par_queryset.get(pk=opt_id)
                        m_goods_info.multiple_par_options.add(options)
                    # 如果是字典则认为是单行文本框
                    if isinstance(opt_id, dict):
                        options_id = opt_id['id']
                        opts = SpecificationParameter.objects.get(pk=options_id)
                        options_value = opt_id['value']
                        ins_opt = ParameterOptions.objects.all().create(control=opts,
                                                                        param_options_name=options_value,
                                                                        param_options_value=options_value)
                        m_goods_info.multiple_par_options.add(ins_opt)

                """
                产品标签
                """
                # 根据id查询
                goods_tag_id = self.initial_data['m_goods_tag']
                tag_list = []
                for good_tag_id in goods_tag_id:
                    good_tag = TagClass.objects.all().get(pk=good_tag_id)
                    if good_tag:
                        tag_list.append(good_tag)
                m_goods_info.m_goods_tag = tag_list
                '''
                成员单品
                '''
                s_goods = self.initial_data['s_goods']
                good_list = []
                for s_good in s_goods:
                    goods = SingleGoods.objects.all().get(pk=s_good)
                    if s_good:
                        good_list.append(goods)
                m_goods_info.s_goods = good_list

                '''
                产品图片
                '''
                m_de_goods = self.initial_data['m_de_goods']
                m_de_img_list = []
                for m_de_good in m_de_goods:
                    m_de_img_list.append(DetailImage(m_de_goods=m_goods_info, image=m_de_good['src']))
                DetailImage.objects.bulk_create(m_de_img_list)

                m_in_goods = self.initial_data['m_in_goods']
                m_in_img_list = []
                for m_in_good in m_in_goods:
                    m_in_img_list.append(IntroduceImage(m_in_goods=m_goods_info, image=m_in_good['src']))
                IntroduceImage.objects.bulk_create(m_in_img_list)

                m_su_goods = self.initial_data['m_su_goods']
                m_su_img_list = []
                for m_su_good in m_su_goods:
                    m_su_img_list.append(SuccessCaseImage(m_su_goods=m_goods_info, image=m_su_good['src']))
                SuccessCaseImage.objects.bulk_create(m_su_img_list)

                m_goods_info.save()
                return m_goods_info

        except Exception as e:
            log.error(e)
            raise TypeError(e)

    def update(self, instance, validated_data):
        instance = super(MultipleGoodsSerializer, self).update(instance, validated_data)

        """
        产品规格参数
        """
        # parameter_id 这个键的值是一个列表
        instance.multiple_par_options.clear()
        parameter = self.initial_data['multiple_par_options']
        par_queryset = ParameterOptions.objects.all()
        for opt_id in parameter:
            if (not isinstance(opt_id, int)) and (not isinstance(opt_id, dict)):
                continue
            # 如果是id则为下拉列表框
            if isinstance(opt_id, int):
                options = par_queryset.get(pk=opt_id)
                instance.multiple_par_options.add(options)
            # 如果是字典则认为是单行文本框
            if isinstance(opt_id, dict):
                options_id = opt_id['id']
                opts = SpecificationParameter.objects.get(pk=options_id)
                options_value = opt_id['value']
                ins_opt = ParameterOptions.objects.all().create(control=opts,
                                                                param_options_name=options_value,
                                                                param_options_value=options_value)
                instance.multiple_par_options.add(ins_opt)
        """
        产品标签
        """
        instance.m_goods_tag.clear()
        goods_tag_list = self.initial_data['m_goods_tag']
        tag_list = []
        for goods_tag in goods_tag_list:
            tag = TagClass.objects.all().get(pk=goods_tag['id'])
            if tag:
                tag_list.append(tag)
        instance.m_goods_tag = tag_list
        """
        成员单品
        """
        instance.s_goods.clear()
        parent_list = self.initial_data['s_goods']
        good_list = []
        for parent in parent_list:
            good = SingleGoods.objects.all().get(pk=parent)
            if good:
                good_list.append(good)
        instance.s_goods = good_list
        """
        产品图片
        """
        instance.m_de_goods.clear()
        detail_img_list = self.initial_data['m_de_goods']
        de_img_list = []
        for de_img in detail_img_list:
            de_img_list.append(DetailImage(m_de_goods=instance, image=de_img['image'], weight=de_img['weight']))
        DetailImage.objects.bulk_create(de_img_list)

        instance.m_in_goods.clear()
        introduce_img_list = self.initial_data['m_in_goods']
        in_img_list = []
        for in_img in introduce_img_list:
            in_img_list.append(IntroduceImage(m_in_goods=instance, image=in_img['image']))
        IntroduceImage.objects.bulk_create(in_img_list)

        instance.m_su_goods.clear()
        success_img_list = self.initial_data['m_su_goods']
        su_img_list = []
        for su_img in success_img_list:
            su_img_list.append(SuccessCaseImage(m_su_goods=instance, image=su_img['image']))
        SuccessCaseImage.objects.bulk_create(su_img_list)

        instance.save()
        return instance


class AdvertisingSerializer(serializers.ModelSerializer):
    """
    广告序列化
    """
    ad_put_operator = serializers.CharField(source='ad_put_operator.last_name', read_only=True)

    class Meta:
        model = Advertising
        fields = ('id', 'ad_position', 'ad_name', 'ad_image', 'ad_put_recent_on',
                  'ad_put_off', 'ad_put_operator', 'ad_status')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                ad_info = super(AdvertisingSerializer, self).create(validated_data)
                # 默认上架人是登录者
                ad_info.ad_put_operator = self.context["request"].user
                ad_info.save()
                return ad_info
        except Exception as e:
            log.error(e)
            raise TypeError(e)

    def update(self, instance, validated_data):
        instance = super(AdvertisingSerializer, self).update(instance, validated_data)
        instance = super(AdvertisingSerializer, self).update(instance, validated_data)
        if instance.ad_put_recent_on <= datetime.date.today():
            instance.ad_status = 1
            instance.save()
        if instance.ad_put_off <= datetime.date.today():
            instance.ad_status = 2
            instance.save()
        return instance


class ViewOpenFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionInfo
        fields = ('id', 'func_name')


class ViewSingleGoodsSerializer(serializers.ModelSerializer):
    """
    前置产品接口序列化
    """
    class Meta:
        model = SingleGoods
        fields = ('id', 'parent', 'goods_name')
