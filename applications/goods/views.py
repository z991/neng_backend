import time
import boto3
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from libs.hash import get_md5
from django.core.files.uploadedfile import UploadedFile

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from .models import MultipleGoods, TagClass, GoodsModel, SingleGoods, Advertising,\
    SpecificationParameter, ParameterOptions
from .serializers import AdvertisingSerializer
from applications.goods.serializers import SingleGoodsSerializer, SimpSingleGoodsSerializer,\
    GoodsModelSerializer, TagClassSerializer, MultipleGoodsSerializer,\
    SimpMultipleGoodsSerializer, SingleGoodsListSerializer,\
    ViewSelectionSerializer, ViewSingleGoodsSerializer, ViewOpenFunctionSerializer,\
    ViewSpecificationParameterSerializer, ListAndGetSpecificationParameterSerializer

from applications.production_manage.models import FunctionInfo, Product, SingleSelection
from applications.production_manage.serializers import SimpProductSerializer
from django.contrib.auth import get_user_model
from applications.setup.permissions import SingleGoodsGroupPermission, AdvertisingGroupPermission,\
    MultipleGoodsGroupPermission, PutawayGroupPermission, GoodsModelGroupPermission, TagClassGroupPermission
from applications.log_manage.models import OperateLog

import datetime
from libs.datetimes import str_to_date
User = get_user_model()
put_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))

today = datetime.date.today()


class SingleMultipleSet(viewsets.ReadOnlyModelViewSet):
    '''
    组合页面的单品下拉列表
    '''
    queryset = SingleGoods.objects.all().order_by("-id")
    serializer_class = SingleGoodsListSerializer
    permission_classes = [MultipleGoodsGroupPermission]

    def get_queryset(self):
        queryset = SingleGoods.objects.all().order_by('-id')
        goods_name = self.request.GET.get('goods_name', "").strip()

        if goods_name:
            queryset = queryset.filter(goods_name__icontains=goods_name)
        return queryset


# 模块配置
class GoodsModelSet(viewsets.ModelViewSet):
    '''
    商品所属模块
    '''
    queryset = GoodsModel.objects.all().order_by("-id")
    serializer_class = GoodsModelSerializer
    permission_classes = [GoodsModelGroupPermission]

    def get_queryset(self):
        queryset = GoodsModel.objects.all().order_by('-id')
        good_model = self.request.GET.get('model_name', "").strip()

        if good_model:  # 商品分类名称查询
            queryset = queryset.filter(model_name__icontains=good_model)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            for dd in data:
                parent_id = dd.get('good_parents', '')
                if parent_id is not None:
                    goods_parent = GoodsModel.objects.get(pk=parent_id)
                    goods_parent = str(goods_parent)
                    dd.update({"good_parents": goods_parent})

            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for dd in data:
            parent_id = dd.get('good_parents', '')
            if parent_id is not None:
                goods_parent = GoodsModel.objects.get(pk=parent_id)
                goods_parent = str(goods_parent)
                dd.update({"good_parents": goods_parent})
        return Response(data)

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(GoodsModelSet, self).create(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': '该模块已存在', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            super(GoodsModelSet, self).update(request, *args, **kwargs)
            OperateLog.create_log(request)
            return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': '该模块已存在', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs
        model_query = GoodsModel.objects.all()
        model_num = model_query.filter(good_parents=pk['pk']).count()
        if model_num >0:
            return Response({'error': '该模块含有子类无法删除'}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return super(GoodsModelSet, self).destroy(request, *args, **kwargs)


class FilterModelSet(viewsets.ReadOnlyModelViewSet):
    '''
    模块父类
    '''
    queryset = GoodsModel.objects.exclude(good_parents__isnull=False).order_by("-id")
    serializer_class = GoodsModelSerializer
    permission_classes = [GoodsModelGroupPermission]

    def get_queryset(self):
        queryset = GoodsModel.objects.exclude(good_parents__isnull=False).order_by("-id")
        good_model = self.request.GET.get('model_name', "").strip()

        if good_model:  # 商品分类名称查询
            queryset = queryset.filter(model_name__icontains=good_model)
        return queryset


# 标签配置
class TagManageSet(viewsets.ModelViewSet):
    queryset = TagClass.objects.all().order_by("-id")
    serializer_class = TagClassSerializer
    permission_classes = [TagClassGroupPermission]

    def get_queryset(self):
        queryset = TagClass.objects.all().order_by('-id')
        label_category = self.request.GET.get('label_category', '').strip()
        goods_tag = self.request.GET.get('goods_tag', '').strip()

        if goods_tag:
            queryset = queryset.filter(goods_tag__icontains=goods_tag)
        if label_category:
            queryset = queryset.filter(label_category=label_category)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(TagManageSet, self).create(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': '该标签已存在', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            super(TagManageSet, self).update(request, *args, **kwargs)
            OperateLog.create_log(request)
            return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': '该标签已存在', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(TagManageSet, self).destroy(request, *args, **kwargs)


class SingleProductManageset(viewsets.ModelViewSet):
    queryset = SingleGoods.objects.all().order_by('-id')
    permission_classes = [SingleGoodsGroupPermission]

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return SimpSingleGoodsSerializer
        else:
            return SingleGoodsSerializer

    def get_queryset(self):
        queryset = SingleGoods.objects.all().order_by('-id')
        goods_sn = self.request.GET.get('goods_sn', "").strip()
        goods_model = self.request.GET.get('goods_model', "").strip()
        goods_name = self.request.GET.get('goods_name', "").strip()

        if goods_name:
            queryset = queryset.filter(goods_name__icontains=goods_name)
        if goods_sn:
            queryset = queryset.filter(goods_sn__icontains=goods_sn)
        if goods_model:
            queryset = queryset.filter(goods_model__model_name__icontains=goods_model)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        for func_name_list in serializer.data['goods_selection']:
            pro = FunctionInfo.objects.all().filter(pk=func_name_list['function']).select_related('product') \
                .values_list('product__product', 'func_name')
            func_name_list['fun_name'] = list(pro)[0][1]
            func_name_list['product'] = list(pro)[0][0]
        for opts in serializer.data['par_options']:
            if isinstance(opts, dict):
                file_list = ParameterOptions.objects.filter(pk=opts['id'])\
                    .select_related('control__file_name', 'control__fill_control')\
                    .values_list('control__id', 'control__fill_control')
                control_id, control_type = file_list[0]
                opts['control_id'] = control_id
                opts['control_type'] = control_type
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                self.perform_create(serializer)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(SingleGoodsSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        today = datetime.date.today()
        pk = kwargs
        goods_query = SingleGoods.objects.all()
        sings1 = goods_query.filter(parent=pk['pk']).count()
        putaway_off_time = goods_query.filter(pk=pk['pk'])\
            .values_list('putaway_off_time', flat=True)
        if putaway_off_time:
            if putaway_off_time[0] >= today:
                return Response({'error': '该商品已经上架，请下架后再删除'}, status=status.HTTP_400_BAD_REQUEST)
        if sings1 > 0:
            return Response({'error': '该商品含有子类无法删除'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            OperateLog.create_log(request)
            return super(SingleProductManageset, self).destroy(request, *args, **kwargs)


class MultipleProductManageset(viewsets.ModelViewSet):
    '''
    组合商品配置
    '''
    queryset = MultipleGoods.objects.all().order_by('-id')
    permission_classes = [MultipleGoodsGroupPermission]

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return SimpMultipleGoodsSerializer
        else:
            return MultipleGoodsSerializer

    def get_queryset(self):
        queryset = MultipleGoods.objects.all().order_by('-id')
        m_goods_sn = self.request.GET.get('m_goods_sn', "").strip()
        m_goods_model = self.request.GET.get('m_goods_model', "").strip()
        m_goods_name = self.request.GET.get('m_goods_name', "").strip()

        if m_goods_name:
            queryset = queryset.filter(m_goods_name__icontains=m_goods_name)
        if m_goods_sn:
            queryset = queryset.filter(m_goods_sn__icontains=m_goods_sn)
        if m_goods_model:
            queryset = queryset.filter(m_goods_model__icontains=m_goods_model)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        for opts in serializer.data['multiple_par_options']:
            if isinstance(opts, dict):
                file_name_list = ParameterOptions.objects.filter(pk=opts['id'])\
                    .select_related('control__file_name', 'control__fill_control')\
                    .values_list('control__id', 'control__fill_control')
                control_id, control_type = file_name_list[0]
                opts['control_id'] = control_id
                opts['control_type'] = control_type
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        goods_data = request.data
        serializer = self.get_serializer(data=goods_data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                self.perform_create(serializer)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(MultipleGoodsSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        today = datetime.date.today()
        putaway_off_time = MultipleGoods.objects.all().filter(pk=kwargs['pk'])\
            .values_list('putaway_off_time', flat=True)
        if putaway_off_time[0] >= today:
            return Response({'error': '该商品已经上架，请下架后再删除'}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return super(MultipleProductManageset, self).destroy(request, *args, **kwargs)


# 广告管理
class AdvertisingViewSet(viewsets.ModelViewSet):
    queryset = Advertising.objects.all()
    serializer_class = AdvertisingSerializer
    permission_classes = [AdvertisingGroupPermission]

    def get_queryset(self):
        queryset = Advertising.objects.all().order_by('-id')

        ad_position = self.request.GET.get('ad_position', "").strip()
        ad_name = self.request.GET.get('ad_name', "").strip()
        ad_put_recent_on = self.request.GET.get('ad_put_recent_on', "").strip()
        ad_put_operator = self.request.GET.get('ad_put_operator', "").strip()
        ad_status = self.request.GET.get('ad_status', "").strip()

        # 操作人
        if ad_put_operator and ad_put_operator != 'undefined':
            queryset = queryset.filter(ad_put_operator__last_name__icontains=ad_put_operator)
        # 广告名称
        if ad_name and ad_name != 'undefined':
            queryset = queryset.filter(ad_name__icontains=ad_name)
        # 位置
        if ad_position and ad_position != 'undefined':
            queryset = queryset.filter(ad_position__icontains=ad_position)
        # 上架时间
        if ad_put_recent_on and ad_put_recent_on != 'undefined':
            queryset = queryset.filter(ad_put_recent_on__icontains=ad_put_recent_on)
        # 上架状态
        if ad_status and ad_status != 'undefined':
            queryset = queryset.filter(ad_status__icontains=ad_status)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if request.user not in User.objects.all():
            return Response({'error': '亲,请先登录!'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        OperateLog.create_log(request)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def update(self, request, *args, **kwargs):
        data = request.data
        if int(data['ad_position']) == 0 and int(data['ad_status']) == 1:
            ad_instance = Advertising.objects.all().filter(ad_position=0, ad_status=1)
            ad_nums = ad_instance.count()
            if ad_nums >= 5 and (Advertising.objects.get(pk=data['id']) not in ad_instance):
                return Response({'error': '已经上架的首页轮播超过五个'}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(AdvertisingSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ad_status = Advertising.objects.all().filter(pk=kwargs['pk']) \
            .values_list('ad_status', flat=True)
        if ad_status[0] == 1:
            return Response({'error': '该商品已经上架，请下架后再删除'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        OperateLog.create_log(request)
        return Response(status=status.HTTP_200_OK)


# 产品规格参数
class SpecificationParameterViewSet(viewsets.ModelViewSet):
    queryset = SpecificationParameter.objects.all()

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return ListAndGetSpecificationParameterSerializer
        else:
            return ViewSpecificationParameterSerializer

    def get_queryset(self):
        queryset = SpecificationParameter.objects.all().order_by('-id')
        file_name = self.request.GET.get('file_name', "").strip()
        param_model = self.request.GET.get('param_model', "").strip()

        if file_name:
            queryset = queryset.filter(file_name__icontains=file_name)
        if param_model:
            queryset = queryset.filter(param_model__model_name__icontains=param_model)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        ret = dict(serializer.data)
        ret['param_model'] = ret['param_model']['id']
        return Response(ret)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # OperateLog.create_log(request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        OperateLog.create_log(request)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 控件下属选项如果在产品参数配置中不允许删除
        number1 = SingleGoods.objects.all().filter(par_options__control=instance).count()
        number2 = MultipleGoods.objects.all().filter(multiple_par_options__control=instance).count()
        if (number1 > 0) or (number2 > 0):
            return Response({'error': '该规格参数正在使用中无法删除'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        # OperateLog.create_log(request)
        return Response(status=status.HTTP_200_OK)


# 广告上架
@api_view(['GET'])
def ad_put(request):
    ad_id = request.GET.get('ad_id', '').strip()
    instance = Advertising.objects.all().get(pk=ad_id)
    # 判断是否是首页轮播图
    if instance.ad_position == 1:
        # 下架操作
        if instance.ad_status == 1:
            instance.ad_status = 2
            instance.ad_put_off = put_time
            instance.save()
            return Response(status=status.HTTP_200_OK)
        else:
            ad_nums = Advertising.objects.all().filter(ad_position=0, ad_status=1).count()
            # 下架状态的广告要上架,必须满足已经上架的没超过五个
            if instance.ad_status == 2 and ad_nums < 5:
                instance.ad_status = 1
                instance.ad_put_recent_on = put_time
                instance.save()
                return Response(status=status.HTTP_200_OK)
            elif instance.ad_status == 3 and ad_nums < 5:
                return Response({'reminder': '是否提前上架'}, status=status.HTTP_200_OK)
            elif ad_nums >= 5:
                return Response({'error': '已经上架的首页轮播超过五个'}, status=status.HTTP_400_BAD_REQUEST)

    # 不是首页轮播图暂时没有上架数量限制
    else:
        if instance.ad_status == 1:
            instance.ad_status = 2
            instance.ad_put_off = put_time
            instance.save()
            return Response(status=status.HTTP_200_OK)
        else:
            # ad_nums = Advertising.objects.all().filter(ad_position=0, ad_status=1).count()
            if instance.ad_status == 2:
                instance.ad_status = 1
                instance.ad_put_recent_on = put_time
                instance.save()
                return Response(status=status.HTTP_200_OK)
            elif instance.ad_status == 3:
                return Response({'reminder': '是否提前上架'}, status=status.HTTP_200_OK)


# 提前上架
@api_view(['GET'])
def ad_time(request):
    ad_id = request.GET.get('ad_id', '').strip()
    ins = Advertising.objects.all()
    instance = ins.get(pk=ad_id)
    # 判断是否是首页轮播图
    if instance.ad_position == 1:
        ad_nums = ins.filter(ad_position=0, ad_status=1).count()
        if ad_nums >= 5:
            return Response({'error': '已经上架的首页轮播超过五个'}, status=status.HTTP_400_BAD_REQUEST)

    # 不是首页轮播图暂时没有上架数量限制 上架首页轮播图少于五个可以上架
    instance.ad_status = 1
    instance.ad_put_recent_on = put_time
    instance.save()
    OperateLog.create_log(request)
    return Response(status=status.HTTP_200_OK)


# 已添加的组合成员单品列表
@api_view(['GET'])
def Members_list(request):
    ret = []
    try:
        single_id = dict(request.GET)['id']
        id_list = []
        for ids in single_id:
            if ids in id_list:
                continue
            else:
                id_list.append(ids)
        for id in id_list:
            good_instance = SingleGoods.objects.all().filter(pk=id)
            good = SimpSingleGoodsSerializer(good_instance, many=True)
            if []:
                ret = good.data
            else:
                for i in good.data:
                    ret.append(i)
        return Response(ret, status=status.HTTP_200_OK)
    except:
        return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def label_list(request):
    """
    标签下拉接口
    """
    label_category = request.GET.get('label_category', '').strip()
    ret = {'data': []}
    tagclass = TagClass.objects.all().filter(label_category=label_category)
    tags = TagClassSerializer(tagclass, many=True)
    for tag in tags.data:
        ret['data'].append(tag)
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def product_list(request):
    """
    产品列表
    产品名称/功能开关名称/功能开关选项值
    参数： 不给 /选定产品id / 选定功能开关id
    """
    ret = []
    goods = Product.objects.all().filter(classify=2)
    pro = SimpProductSerializer(goods, many=True)
    ret.append(pro.data)
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def function_list(request):
    """
    功能开关 给我一个product_id   不是单品id
    """
    func_id = request.GET.get('goods_id', '').strip()
    ret = []
    func_instance = FunctionInfo.objects.all().filter(product_id=func_id)
    func_list = ViewOpenFunctionSerializer(func_instance, many=True)
    for func in func_list.data:
        ret.append(func)
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def selection_list(request):
    """
    功能开关选项
    """
    function_id = request.GET.get('function_id', '').strip()
    ret = []
    func = SingleSelection.objects.all().filter(function_id=function_id)
    tags = ViewSelectionSerializer(func, many=True)
    for tag in tags.data:
        ret.append(tag)
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def parent_list(request):
    """
    前置产品
    """
    ret = []
    parent = SingleGoods.objects.all()
    par = ViewSingleGoodsSerializer(parent, many=True)
    ret.append(par.data)
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def models_list(request):
    """
    所属商品模块
    """
    ret = []
    models = GoodsModel.objects.all()
    par = GoodsModelSerializer(models, many=True)
    mods = par.data
    for mod in mods:
        ret.append(mod)
    return Response(ret, status=status.HTTP_200_OK)


@csrf_exempt
def get_editor(request):
    """富文本上传jpeg图片，返回该图片的url"""
    if not request.method == "POST":
        return JsonResponse({"error": "request method not allowed"}, status=status.HTTP_400_BAD_REQUEST)
    cli = boto3.client(**settings.BAISHANYUN_CONFIGS)  # 获得客户端会话对象

    file = request.FILES['myFileName']
    assert isinstance(file, UploadedFile)  # 获取到的文件信息应为一个UploadedFile对象

    file_type = file.name.split(".")[-1]
    if file_type not in ("jpg", "jpeg", "png"):
        return JsonResponse({"error": "文件格式不合法，目前只支持jpeg, jpg, png"}, status=status.HTTP_400_BAD_REQUEST)
    data = file.read()
    key = get_md5(data)
    cli.put_object(
        ACL='public-read',  # 公共可读
        Bucket='minioss',  # 固定
        Key=f"oa/{key}.jpeg",  # 文件保存在oa目录下
        ContentType=f'image/jpeg',
        Body=data
    )
    url = f'http://s2.i.qingcdn.com/minioss/oa/{key}.jpeg'
    return HttpResponse((json.dumps(url)))


# 上架新增&修改接口
@api_view(['POST', 'PUT'])
@permission_classes([PutawayGroupPermission, ])
def create_put_up(request):
    today = datetime.date.today()
    bod = request.body
    bod = str(bod, encoding="utf-8")
    bod = json.loads(bod)
    goods_sn = bod.get('goods_sn', '')
    on_time = bod.get('putaway_recent_on_time', '1970-01-01').strip()
    off_time = bod.get('putaway_off_time', '1970-01-01').strip()
    sell_status = bod.get('sell_status', '1')
    recommend = bod.get('recommend', '2')
    put_price = bod.get('put_price', '0')
    goods_price = bod.get('goods_price', '')
    user = request.user.last_name
    on_time = str_to_date(on_time)
    off_time = str_to_date(off_time)

    today = datetime.date.today()

    # 判断请求方式以及上架状态
    if (request.method == 'PUT') and (on_time <= today) and (off_time > today):
        return Response({'error': '上架商品无法修改,请先下架'}, status=status.HTTP_400_BAD_REQUEST)

    # 单品上架新增信息
    s_goods_info = {
        "putaway_recent_on_time": on_time,
        "putaway_off_time": off_time,
        "sell_status": sell_status,
        "recommend": recommend,
        "put_price": put_price,
        "putaway_operator": user,
        "goods_price": goods_price
    }

    # 组合商品上架新增信息
    m_goods_info = {
        "putaway_recent_on_time": on_time,
        "putaway_off_time": off_time,
        "sell_status": sell_status,
        "recommend": recommend,
        "put_price": put_price,
        "putaway_operator": user,
    }

    if goods_sn[0] == 'A':
        res = SingleGoods.objects.filter(goods_sn=goods_sn).update(**s_goods_info)
    if goods_sn[0] == 'B':
        res = MultipleGoods.objects.filter(m_goods_sn=goods_sn).update(**m_goods_info)
    OperateLog.create_log(request)
    return Response({"info": "上架成功"}, status=status.HTTP_200_OK)


# 上架查看接口
@api_view(['GET'])
@permission_classes([PutawayGroupPermission, ])
def list_put_up(request):
    today = datetime.date.today()
    # 过滤上架时间是1970-01-01的产品
    put_single = SingleGoods.objects.all().exclude(putaway_recent_on_time='1970-01-01').order_by('-putaway_recent_on_time')
    put_multiple = MultipleGoods.objects.all().exclude(putaway_recent_on_time='1970-01-01').order_by('-putaway_recent_on_time')

    # 页码
    page = request.GET.get('page', 1)
    page = int(page)
    # 商品编码
    goods_sn = request.GET.get('goods_sn', '').strip()
    # 商品名字
    goods_name = request.GET.get('goods_name', '').strip()
    # 商品属性
    goods_attribute = request.GET.get('goods_attribute', '').strip()
    # 售卖状态
    sell_status = request.GET.get('sell_status', '').strip()
    # 操作人
    putaway_operator = request.GET.get('putaway_operator', '').strip()
    # 最近上架时间
    putaway_recent_on_time = request.GET.get('putaway_recent_on_time', '').strip()
    # 上架状态
    putaway_on_status = request.GET.get('putaway_on_status', '').strip()
    # 下架时间
    putaway_off_time = request.GET.get('putaway_off_time', '').strip()

    if goods_sn:
        put_single = put_single.filter(goods_sn__icontains=goods_sn)
        put_multiple = put_multiple.filter(m_goods_sn__icontains=goods_sn)
    if goods_name:
        put_single = put_single.filter(goods_name__icontains=goods_name)
        put_multiple = put_multiple.filter(m_goods_name__icontains=goods_name)
    if sell_status:
        put_single = put_single.filter(sell_status=sell_status)
        put_multiple = put_multiple.filter(sell_status=sell_status)
    if putaway_on_status == '1':#上架
        put_single = put_single.filter(putaway_recent_on_time__lte=today,
                                       putaway_off_time__gt=today)
        put_multiple = put_multiple.filter(putaway_recent_on_time__lte=today,
                                           putaway_off_time__gt=today)
    if putaway_on_status == '2':#下架
        put_single = put_single.filter(putaway_off_time__lte=today)
        put_multiple = put_multiple.filter(putaway_off_time__lte=today)
    if putaway_on_status == '3':#待上架
        put_single = put_single.filter(putaway_recent_on_time__gt=today, putaway_off_time__gt=today)
        put_multiple = put_multiple.filter(putaway_recent_on_time__gt=today, putaway_off_time__gt=today)
    if putaway_operator:
        put_single = put_single.filter(putaway_operator=putaway_operator)
        put_multiple = put_multiple.filter(putaway_operator=putaway_operator)
    if putaway_recent_on_time:
        put_single = put_single.filter(putaway_recent_on_time=putaway_recent_on_time)
        put_multiple = put_multiple.filter(putaway_recent_on_time=putaway_recent_on_time)
    if putaway_off_time:
        put_single = put_single.filter(putaway_off_time=putaway_off_time)
        put_multiple = put_multiple.filter(putaway_off_time=putaway_off_time)

    # 获取总条数
    count1 = put_single.count()
    count2 = put_multiple.count()
    total_count = count1+count2
    # 获取总页数
    total_page = total_count//10
    total_page = total_page+1

    result_s = []
    index_s = 0
    for single in put_single:
        s_on_time = single.putaway_recent_on_time
        s_off_time = single.putaway_off_time
        if s_on_time <= today and s_off_time > today:
            putaway_on_status = "上架"
        elif (s_on_time <= today and s_off_time <= today) or  (s_off_time <= today):
            putaway_on_status = "下架"
        elif s_on_time > today and s_off_time <=today:
            putaway_on_status = "下架"
        elif s_on_time > today and s_off_time > today:
            putaway_on_status = "待上架"
        index_s += 1
        result_s.append(
            {"id": single.id,
             "putaway_recent_on_time": s_on_time,
             "put_price": single.put_price,
             "putaway_on_status": putaway_on_status,
             "sell_status": single.sell_status,
             "putaway_off_time": s_off_time,
             "putaway_operator": single.putaway_operator,
             "goods_sn": single.goods_sn,
             "goods_name": single.goods_name,
             "recommend": single.recommend,
             "goods_price": single.goods_price,
             "goods_attribute": "单件商品",
             "index": index_s
             }
        )

    index_m = count1-1
    result_m = []
    for multiple in put_multiple:
        m_on_time = multiple.putaway_recent_on_time
        m_off_time = multiple.putaway_off_time
        if m_off_time <= today:
            putaway_on_status = "下架"
        elif m_on_time <= today and m_off_time > today:
            putaway_on_status = "上架"
        elif m_on_time > today:
            putaway_on_status = "待上架"
        index_m += 1

        result_m.append(
            {"id": multiple.id,
             "putaway_recent_on_time": m_on_time,
             "put_price": multiple.put_price,
             "putaway_on_status": putaway_on_status,
             "sell_status": multiple.sell_status,
             "putaway_off_time": m_on_time,
             "putaway_operator": multiple.putaway_operator,
             "goods_sn": multiple.m_goods_sn,
             "goods_name": multiple.m_goods_name,
             "recommend": multiple.recommend,
             "goods_attribute": "组合商品",
             "index": index_m
             }
        )
    if page == 1:
        start = 0
        end = 10
    else:
        start = 10 * (page - 1)
        end = 10 * page

    if goods_attribute == '1':
        result_s = result_s[start:end]
        return Response({"total_count": count1, "total_page": total_page, "results": result_s}, status=status.HTTP_200_OK)
    elif goods_attribute == '2':
        result_m = result_m[start:end]
        return Response({"total_count": count2, "total_page": total_page, "results": result_m}, status=status.HTTP_200_OK)
    result = result_s.extend(result_m)
    result_s = result_s[start:end]
    return Response({"total_count": total_count, "total_page": total_page, "results": result_s}, status=status.HTTP_200_OK)


# 上架商品选择接口
@api_view(['GET'])
@permission_classes([PutawayGroupPermission, ])
def put_goods(request):
    put_single = SingleGoods.objects.all().filter(putaway_recent_on_time='1970-01-01')
    put_multiple = MultipleGoods.objects.all().filter(putaway_recent_on_time='1970-01-01')

    goods_name = request.GET.get('goods_name', '').strip()
    sid = request.GET.get('sid', '')

    if sid == '1' and goods_name:
        put_single = put_single.filter(goods_name__icontains=goods_name)
    if sid == '2' and goods_name:
        put_multiple = put_multiple.filter(m_goods_name__icontains=goods_name)

    result_s = []
    for single in put_single:
        result_s.append(
            {"id": single.id,
             "goods_name": single.goods_name,
             "goods_sn": single.goods_sn
             })

    result_m = []
    for multiple in put_multiple:
        result_m.append(
            {
                "id":multiple.id,
                "goods_name": multiple.m_goods_name,
                "goods_sn":multiple.m_goods_sn
            }
        )

    count1 = put_single.count()
    count2 = put_multiple.count()

    total_page1 = count1//10+1
    total_page2 = count2//10+1

    if sid == '1':
        return Response({"total_count": count1, "total_page": total_page1, "results": result_s},status=status.HTTP_200_OK)
    if sid == '2':
        return Response({"total_count": count2, "total_page": total_page2, "results": result_m}, status=status.HTTP_200_OK)


# 上架删除操作接口
@api_view(['DELETE'])
@permission_classes([PutawayGroupPermission, ])
def delete_put(request):
    goods_sn = request.GET.get('goods_sn', '')
    putaway_on_status = request.GET.get('putaway_on_status', '')

    # 单品
    if putaway_on_status == '上架' and goods_sn:
        return Response({'error': '上架商品无法修改,请先下架'}, status=status.HTTP_400_BAD_REQUEST)
    if goods_sn[0] == 'A' and putaway_on_status is not '上架':
        ret = SingleGoods.objects.filter(goods_sn=goods_sn).update(putaway_recent_on_time='1970-01-01',
                                                          putaway_off_time='1970-01-01')
    elif goods_sn[0] == 'B' and putaway_on_status is not '上架':
        ret = MultipleGoods.objects.filter(m_goods_sn=goods_sn).update(putaway_recent_on_time='1970-01-01',
                                                          putaway_off_time='1970-01-01')
    OperateLog.create_log(request)
    return Response({"info": "删除成功"}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([PutawayGroupPermission, ])
def put_up(request):
    """
    上架操作
    """
    today = datetime.date.today()
    bod = request.body
    bod = str(bod, encoding="utf-8")
    bod = json.loads(bod)

    goods_sn = bod.get('goods_sn', None)
    putaway_recent_on_time = bod.get('on_time', '1970-01-01')
    putaway_off_time = bod.get('off_time', None)

    if goods_sn[0] == 'A':
        up1 = SingleGoods.objects.filter(goods_sn=goods_sn).update(putaway_recent_on_time=putaway_recent_on_time,
                                                  putaway_off_time=putaway_off_time)
    elif goods_sn[0] == 'B':
        up1 = MultipleGoods.objects.filter(m_goods_sn=goods_sn).update(putaway_recent_on_time=putaway_recent_on_time,
                                                   putaway_off_time=putaway_off_time)
    OperateLog.create_log(request)
    return Response(status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([PutawayGroupPermission, ])
def put_off(request):
    """
    下架操作
    """
    today = datetime.date.today()
    bod = request.body
    bod = str(bod, encoding="utf-8")
    bod = json.loads(bod)
    goods_sn = bod.get('goods_sn', None)
    if goods_sn[0] == 'A':
        off = SingleGoods.objects.filter(goods_sn=goods_sn).update(putaway_off_time=today)
    if goods_sn[0] == 'B':
        off = MultipleGoods.objects.filter(m_goods_sn=goods_sn).update(putaway_off_time=today)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def test_put(request):
    ret1 = SingleGoods.objects.all().update(putaway_recent_on_time="2018-05-01", putaway_off_time="2020-05-01")
    ret2 = MultipleGoods.objects.all().update(putaway_recent_on_time="2018-05-01", putaway_off_time="2020-05-01")
    return Response(status=status.HTTP_200_OK)
