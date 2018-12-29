from functools import reduce

import xlrd
import xlwt
import copy
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from io import BytesIO

from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from applications.data_manage.views import SerGrpInquriesViewSet
from applications.log_manage.models import OperateLog
from applications.log_manage.views import OpenStationViewSet
from applications.production_manage.models import Product, VersionInfo, FunctionInfo, SingleSelection, Server, \
    SerType, ServerGroup, Grid, DataBaseInfo, SerAddress, SerIp
from applications.production_manage.serializers import ProductSerializer, VersionInfoSerializer, \
    SingleSelectionSerializer, ServerSerializer, SerTypeSerializer, \
    GroupSerializer, GridSerializer, DataBaseInfoSerializer, SerAddressSerializer, \
    SimpGroupSerializer, SimpProductSerializer, SimpGridSerializer, ForGroupSerTypeSerializer, \
    SerIpSerializer, ForDateProductSerializer, ForShipGridSerializer, SimpVersionInfoSerializer, \
    ForDetailFunctionSerializer, ForOpenProductSerializer, FunctionInfoSerializer, VersionProductSerializer
from ldap_server.configs import DEPLOY_WAYS, CLI_CHOICES, CLI_UNLIMITED, REFACTOR_VERSION, CLASSIC_VERSION, \
    PROD_SERV_VERSIONS
from libs.database import mysql_test
from libs.hash import decrypt, encrypt
from applications.goods.models import SingleGoods
from applications.production_manage.models import SingleSelection
from applications.workorder_manage.models import OpenStationManage
from applications.setup.permissions import GridGroupPermission, ServerGroupsGroupPermission, \
    ReServerGroupPermission, ServerGroupPermission, ReProductGroupPermission, ProductGroupPermission


# 经典版 产品
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().filter(classify=CLASSIC_VERSION).order_by('-id')
    permission_classes = [ProductGroupPermission]

    def get_serializer_class(self):
        if self.action == 'forgrid':
            return ProductSerializer
        elif self.action == 'foropen':
            return SimpProductSerializer
        elif self.action == 'fordata':
            return ForDateProductSerializer
        elif self.action == 'for_open_func':
            return ForOpenProductSerializer
        elif self.suffix == 'List' and self.request.method == 'GET':
            return VersionProductSerializer
        else:
            return ProductSerializer

    @list_route(methods=['get'])
    def forgrid(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(ProductViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def foropen(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(ProductViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def fordata(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(ProductViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        # 产品中search
        queryset = Product.objects.all().filter(classify=CLASSIC_VERSION).order_by('-id')
        product = self.request.GET.get('product_name', "").strip()  # 获取单个产品
        products = self.request.GET.getlist('product', [])  # 开站时，取功能列表，需传入多个产品ID
        if product:
            queryset = queryset.filter(product__icontains=product)
        if products:
            queryset = queryset.filter(id__in=products)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        data['classify'] = CLASSIC_VERSION
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(ForDateProductSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        data['classify'] = CLASSIC_VERSION
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(ForDateProductSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(ProductViewSet, self).destroy(request, *args, **kwargs)

    @list_route(methods=['GET'])
    def for_open_func(self, request):
        station = request.GET.get('station', '')
        if station == 'post':
            station = ''
        queryset = self.filter_queryset(self.get_queryset())
        base_queryset = queryset.filter(function__func_type='单选框')

        result = base_queryset.select_related('function__id', 'function__func_name', 'function__func_type',
                                              'function__parent', 'function__selection__id',
                                              'function__selection__select_name',
                                              'function__selection__select_value',
                                              'function__selection__is_default',
                                              'function__is_enable') \
            .values_list('id', 'product', 'function__id', 'function__func_name', 'function__func_type',
                         'function__parent', 'function__selection__id', 'function__selection__select_name',
                         'function__selection__select_value', 'function__selection__is_default',
                         'function__is_enable')
        data = []
        for each in result:
            each_list = ['id', 'product', 'func_id', 'func_name', 'func_type', 'parent', 'selec_id',
                         'selec_name', 'selec_value', 'is_default', 'is_enable']
            new_each = dict(zip(each_list, each))
            if new_each['is_enable'] == 0:
                continue
            data.append(new_each)

        product_queryset = Product.objects.all()

        products = request.GET.getlist('product', [])
        product_name = self.request.GET.get('product_name', "").strip()
        if product_name:
            product_queryset = product_queryset.filter(product__icontains=product_name)
        if products:
            product_queryset = product_queryset.filter(id__in=products)
        pro_func_type = product_queryset.select_related('function__func_type')\
            .values_list('id', 'function__func_type')

        product_id_list = []
        product_select_list = []
        for before, after in pro_func_type:
            product_select_list.append(after)
            if after == '文本框':
                product_id_list.append(before)
        if '文本框' in product_select_list:
            for pro in product_id_list:
                inner_queryset = Product.objects.all().filter(pk=pro) \
                    .filter(function__func_type='文本框') \
                    .values_list('id', 'product', 'function__id', 'function__func_name',
                                 'function__func_type', 'function__parent',
                                 'function__selection__select_value', 'function__selection__is_default')

                item_list = ['id', 'product', 'func_id', 'func_name', 'func_type', 'parent',
                             'selec_value', 'is_default']
                inner_dict = dict(zip(item_list, inner_queryset[0]))
                if inner_dict not in data:
                    data.append(inner_dict)
        return Response(data, status=status.HTTP_200_OK)


# 重构版 产品
class RefProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().filter(classify=REFACTOR_VERSION).order_by('-id')
    permission_classes = [ReProductGroupPermission]

    def get_serializer_class(self):
        if self.action == 'forgrid':
            return ProductSerializer
        elif self.action == 'foropen':
            return SimpProductSerializer
        elif self.action == 'fordata':
            return ForDateProductSerializer
        elif self.action == 'for_open_func':
            return ForOpenProductSerializer
        # 列表查询使用的序列化
        elif self.suffix == 'List' and self.request.method == 'GET':
            return VersionProductSerializer
        else:
            return ProductSerializer

    @list_route(methods=['get'])
    def forgrid(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(RefProductViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def foropen(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(RefProductViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def fordata(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(RefProductViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        # 产品中search
        queryset = Product.objects.all().filter(classify=REFACTOR_VERSION).order_by('-id')
        product = self.request.GET.get('product_name', "").strip()  # 获取单个产品
        products = self.request.GET.getlist('product', [])  # 开站点时，取功能列表，需传入多个产品ID
        if product:
            queryset = queryset.filter(product__icontains=product)
        if products:
            queryset = queryset.filter(id__in=products)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        data['classify'] = REFACTOR_VERSION
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(ForDateProductSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        data['classify'] = REFACTOR_VERSION
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(ForDateProductSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs
        id = pk.get('pk')
        id = int(id)
        sings = SingleGoods.objects.all()
        selects = set()
        products = set()
        for i in sings:
            select_id = i.goods_selection.all()
            for j in select_id:
                selects.add(j.id)
        for sele in selects:
            singselect = SingleSelection.objects.get(pk=sele)
            product_id = singselect.function.product.id
            products.add(product_id)
        if id in products:
            return Response({'error': '该产品在使用禁止删除'}, status=status.HTTP_400_BAD_REQUEST)
        OperateLog.create_log(request)
        return super(RefProductViewSet, self).destroy(request, *args, **kwargs)

    @list_route(methods=['get'])
    def for_open_func(self, request):
        station = request.GET.get('station', '')
        if station == 'post':
            station = ''
        queryset = self.filter_queryset(self.get_queryset())
        base_queryset = queryset.filter(function__func_type='单选框')

        result = base_queryset.select_related('function__id', 'function__func_name', 'function__func_type',
                                              'function__parent', 'function__selection__id',
                                              'function__selection__select_name',
                                              'function__selection__select_value',
                                              'function__selection__is_default',
                                              'function__is_enable') \
            .values_list('id', 'product', 'function__id', 'function__func_name', 'function__func_type',
                         'function__parent', 'function__selection__id', 'function__selection__select_name',
                         'function__selection__select_value', 'function__selection__is_default',
                         'function__is_enable')
        data = []
        for each in result:
            each_list = ['id', 'product', 'func_id', 'func_name', 'func_type', 'parent', 'selec_id',
                         'selec_name', 'selec_value', 'is_default', 'is_enable']
            new_each = dict(zip(each_list, each))
            if new_each['is_enable'] == 0:
                continue
            data.append(new_each)

        product_queryset = Product.objects.all()

        products = request.GET.getlist('product', [])
        product_name = self.request.GET.get('product_name', "").strip()
        if product_name:
            product_queryset = product_queryset.filter(product__icontains=product_name)
        if products:
            product_queryset = product_queryset.filter(id__in=products)

        pro_func_type = product_queryset.select_related('function__func_type') \
            .values_list('id', 'function__func_type')
        product_id_list = []
        product_select_list = []
        for before, after in pro_func_type:
            product_select_list.append(after)
            if after == '文本框':
                product_id_list.append(before)
        if '文本框' in product_select_list:
            for pro in product_id_list:
                inner_queryset = Product.objects.all().filter(pk=pro) \
                    .filter(function__func_type='文本框') \
                    .values_list('id', 'product', 'function__id', 'function__func_name',
                                 'function__func_type', 'function__parent',
                                 'function__selection__select_value', 'function__selection__is_default')

                item_list = ['id', 'product', 'func_id', 'func_name', 'func_type', 'parent',
                             'selec_value', 'is_default']
                inner_dict = dict(zip(item_list, inner_queryset[0]))
                if inner_dict not in data:
                    data.append(inner_dict)
        return Response(data, status=status.HTTP_200_OK)


class VersionViewSet(viewsets.ModelViewSet):
    queryset = VersionInfo.objects.all().order_by('-id')
    serializer_class = VersionInfoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        pro_version = data.get("pro_versionp")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(SimpVersionInfoSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
        OperateLog.create_log(request)
        return Response(SimpVersionInfoSerializer(instance).data, status=status.HTTP_200_OK)

    @detail_route(methods=['put'])
    def modify_func(self, request, pk=None):
        function_list = request.data.get('function', [])
        function_set = FunctionInfo.objects.all().filter(id__in=function_list)
        instance = self.get_object()
        with transaction.atomic():
            instance.function.set(function_set)
            instance.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(VersionViewSet, self).destroy(request, *args, **kwargs)


@api_view(['GET'])
def func_selec(request):
    data = SingleSelection.objects.all().values_list('id', 'select_name', 'select_value')

    return Response(data, status=status.HTTP_200_OK)


# 功能
class FunctionViewSet(viewsets.ModelViewSet):
    queryset = FunctionInfo.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.suffix == 'Instance' and self.request.method == 'GET':
            return ForDetailFunctionSerializer
        else:
            return FunctionInfoSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        func = serializer.data['parent']
        if func:
            func_instance = FunctionInfo.objects.all().get(pk=func[0]['function'])
            serializer.data['parent'][0]['function'] = func_instance.func_name
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        selection_info = request.data.pop('selection')
        product = request.data['product']
        classify = Product.objects.get(id=product).classify

        if classify == REFACTOR_VERSION:
            parent_set = []
            depend_set = []
            # 若parent_info有id(代表单选项)有值，则获取这些单选项对象
            parent_info = request.data.pop('parent')
            if 'id' in parent_info.keys() and parent_info['id']:
                parent_set = list(SingleSelection.objects.all().filter(id__in=parent_info['id']))

            # depend_info(代表单选项)有值，则获取这些单选项对象
            depend_info = request.data.pop('dependences')
            if 'id' in depend_info.keys() and depend_info['id']:
                depend_set = list(SingleSelection.objects.all().filter(id__in=depend_info['id']))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()

            selection_list = []  # 存放未真正执行保存的选项对象
            # 取selection信息，创建selection
            for selc_data in selection_info:
                selc_data['function_id'] = instance.id
                if selc_data['is_default'] is not True:
                    selc_data['is_default'] = False
                selec = SingleSelection(**selc_data)
                selection_list.append(selec)
            SingleSelection.objects.bulk_create(selection_list)

            if classify == REFACTOR_VERSION:
                if 'ipu' in parent_info.keys() and parent_info['ipu']:
                    for func_inpt in parent_info['ipu']:
                        for each_inpt in func_inpt['value']:
                            selec, _ = SingleSelection.objects.get_or_create(function_id=func_inpt['id'],
                                                                             select_value=each_inpt, \
                                                                             select_name=each_inpt)
                            parent_set.append(selec)
                instance.parent.set(parent_set)

                if 'ipu' in depend_info.keys() and depend_info['ipu']:
                    for func_inpt in depend_info['ipu']:
                        for each_inpt in func_inpt['value']:
                            selec, _ = SingleSelection.objects.get_or_create(function_id=func_inpt['id'],
                                                                             select_value=each_inpt, \
                                                                             select_name=each_inpt)
                            depend_set.append(selec)
                instance.dependences.set(depend_set)

            instance.save()
        OperateLog.create_log(request)
        return Response(ForDetailFunctionSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        selection_info = request.data.pop('selection')
        product = request.data['product']
        classify = Product.objects.get(id=product).classify

        if classify == REFACTOR_VERSION:
            parent_set = []
            depend_set = []

            # 为添加父级展示条件做准备
            # 若parent_info有id(代表单选项)有值，则获取这些单选项对象
            parent_info = request.data.pop('parent')
            if 'id' in parent_info.keys() and parent_info['id']:
                parent_set = list(SingleSelection.objects.all().filter(id=parent_info['id']))

            # 为添加联动展示条件做准备
            # depend_info(代表单选项)有值，则获取这些单选项对象
            depend_info = request.data.pop('dependences')
            if 'id' in depend_info.keys() and depend_info['id']:
                depend_set = list(SingleSelection.objects.all().filter(id=depend_info['id']))

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instance = serializer.save()
            if classify == REFACTOR_VERSION:
                if 'id' in parent_info.keys() and parent_info['id']:
                    instance.parent.set(parent_set)
                if 'id' in depend_info.keys() and depend_info['id']:
                    instance.dependences.set(depend_set)

            if selection_info:
                selection_list = []  # 不同于新增，这个列表的元素是对象
                # 取selection信息，创建selection
                for selec_data in selection_info:
                    selec_data['function_id'] = instance.id
                    if 'childfunc' in selec_data.keys():
                        del selec_data['childfunc']
                    if selec_data['is_default'] is not True:
                        selec_data['is_default'] = False
                    selec, _ = SingleSelection.objects.update_or_create(
                        defaults=dict(select_value=selec_data['select_value'],
                                      is_default=bool(int(selec_data['is_default']))),
                        function_id=selec_data['function_id'], select_name=selec_data['select_name'])
                    selection_list.append(selec)
                instance.selection.set(selection_list)

            if classify == REFACTOR_VERSION:
                if 'ipu' in parent_info.keys() and parent_info['ipu']:
                    for func_inpt in parent_info['ipu']:
                        for each_inpt in func_inpt['value']:
                            selec, _ = SingleSelection.objects.get_or_create(function_id=func_inpt['id'],
                                                                             select_value=each_inpt, \
                                                                             select_name=each_inpt)
                            parent_set.append(selec)
                instance.parent.set(parent_set)

                if 'ipu' in depend_info.keys() and depend_info['ipu']:
                    for func_inpt in depend_info['ipu']:
                        for each_inpt in func_inpt['value']:
                            selec, _ = SingleSelection.objects.get_or_create(function_id=func_inpt['id'],
                                                                             select_value=each_inpt, \
                                                                             select_name=each_inpt)
                            depend_set.append(selec)
                            instance.dependences.set(depend_set)

                            instance.save()

                            OperateLog.create_log(request)
        return Response(ForDetailFunctionSerializer(instance).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(FunctionViewSet, self).destroy(request, *args, **kwargs)

    @classmethod
    def get_func_tree(cls):
        """ 
        目标数据格式
        (102, 'ref_14_func102', '半开', 45)
        (102, 'ref_14_func102', '关', 45) 
        (102, 'ref_14_func102', '开', 45)
        """
        queryset = FunctionInfo.objects.all() \
            .filter(Q(product__classify=2) & Q(parent__isnull=False)).distinct() \
            .prefetch_related('parent__select_name', 'parent__function', 'parent__function__func_name') \
            .values_list('id', 'parent__function', 'parent__function__func_name', 'parent__select_name')
        """
        目标数据格式
        ((102, 45),('ref_14_func102','开')）
        ((102, 45),('ref_14_func45', '关')
        ((102, 45),('ref_14_func45', '半开'))
        """
        ret = map(lambda x: ((x[0], x[1]), (x[2], x[3])), queryset)

        """
        目标数据格式：
        {(102, 45):[('ref_14_func102','开'),('ref_14_func45', '关'),('ref_14_func45', '半开')]}
        """
        des_dict = {}  # 存储结果的字段
        for key, each_value in ret:
            des_dict.setdefault(key, [])
            des_dict[key].append(each_value)

        """
        目标数据格式：
        {(102, 45):'ref_14_func45:开/半开/关'}
        """
        for key, value in des_dict.items():
            des_dict[key] = reduce(lambda x, y: x + y[1] + '/', value, value[0][0] + ':')
            des_dict[key].strip('/')

        """
        当前数据格式：
        {(45, 102): 'ref_14_func102:/开/半开/关',
         (99, 71): 'ref_12_func71:/2',
         (101, 99): 'ref_12_func99:/2',
         (106, 105): 'ref_17_func105:/ss第三代',
         (108, 101): 'ref_12_func101:/3',
         (113, 45): 'ref_14_func45:/开/关'
         }"""

        src_dict = copy.deepcopy(des_dict)
        parent_map = dict(src_dict.keys())

        def get_parent_list(x):
            """
            function:将键————类似‘(113, 45)’的父级————类似‘(45, 102)’依照"1阶父级，2阶父级，3阶父级……"存入列表
            param: x 需要对应取其父级列表的标的 格式类似：(113, 45): 'ref_14_func45:/开/关'
            return：x 的父级列表  格式类似[((113, 45): 'ref_14_func45:/开/关'), ((45, 100): 'ref_14_func100:/开/关'), ((100, 200): 'ref_14_func200:/开/关')]
            """
            key, value = x
            li = []
            while key[1] in parent_map.keys():
                li.append(((key[1], parent_map[key[1]]), src_dict[(key[1], parent_map[key[1]])]))
                key, value = li[-1]
            return li

        """
        目标数据格式：
        {(45, 102): 'ref_14_func102:开/半开/关/',
         (99, 71): 'ref_12_func71:2/',
         (101, 99): 'ref_12_func71:2/-->ref_12_func99:2/',
         (106, 105): 'ref_17_func105:ss第三代/',
         (108, 101): 'ref_12_func71:2/-->ref_12_func99:2/-->ref_12_func101:3/',
         (113, 45): 'ref_14_func102:开/半开/关/-->ref_14_func45:开/关/'}
        """
        ret = {}
        for each in des_dict.items():
            key, value = each
            li = get_parent_list(each)
            ret[key[0]] = reduce(lambda x, y: y[1] + '-->' + x, li, value)

        func_id_name_map = FunctionInfo.objects.all() \
            .filter(Q(product__classify=2) & Q(parent__isnull=False)).distinct() \
            .values_list('id', 'func_name')
        func_id_name_map = dict(func_id_name_map)

        for id in ret.keys():
            ret[id] = ret[id] + '-->' + func_id_name_map[id]

        return ret

    def get_queryset(self):
        queryset = FunctionInfo.objects.all().order_by('-id')
        parent = int(self.request.GET.get('parent', 0))
        depend = int(self.request.GET.get('depend', 0))
        product = self.request.GET.get('product', 0)  # 产品
        grid = int(self.request.GET.get('grid', 0))  # 节点
        cli_version = int(self.request.GET.get('cli_version', 0))  # 客户版本

        if parent:
            self.pagination_class = None
            queryset = queryset.filter(product_id=product)
        elif depend:
            self.pagination_class = None
            queryset = queryset.filter(product__classify=2).exclude(product_id=product)
        elif product:
            queryset = queryset.filter(product_id=product)

        return queryset.distinct()  # 选项


class SelectionViewSet(viewsets.ModelViewSet):
    queryset = SingleSelection.objects.all().select_related('function').order_by('-id')
    serializer_class = SingleSelectionSerializer

    @detail_route(methods=['put'])
    def modify_default(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        selection = SingleSelection.objects.all() \
            .filter(function__id=instance.function.id,
                    is_default=True)

        with transaction.atomic():
            if selection.exists():
                for selec in selection:
                    selec.is_default = 0
                    selec.save()

            instance.is_default = 1
            instance.save()
        OperateLog.create_log(request)
        return Response({}, status=status.HTTP_200_OK)


# 服务器
class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all().prefetch_related('ser_url').order_by('-id')
    serializer_class = ServerSerializer
    permission_classes = [ServerGroupPermission]

    def get_queryset(self):
        # 服务器中search
        queryset = Server.objects.all().prefetch_related("ser_url", "ser_url__ser_ip", "ser_name").order_by('-id')
        ser_id = self.request.GET.get('ser_id', "").strip()  # 服务器ID
        if ser_id:
            queryset = queryset.filter(ser_id__icontains=ser_id)
        version_type = self.request.GET.get('version_type', None)
        if not version_type:
            version_type = self.request.data['version_type']
            if not version_type:
                version_type = CLASSIC_VERSION
        queryset = queryset.filter(version_type=version_type)
        return queryset

    def valid(self, server_serializer, seraddress_data_list):
        try:
            server_serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        for adrs_data in seraddress_data_list:
            ip_data_list = adrs_data['ser_ip']
            adrs_serializer = SerAddressSerializer(data=adrs_data)
            try:
                adrs_serializer.is_valid(raise_exception=True)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            for ip_data in ip_data_list:
                try:
                    ip_serializer = SerIpSerializer(data=ip_data)
                    ip_serializer.is_valid(raise_exception=True)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        server_data = request.data
        seraddress_data_list = server_data.pop('ser_url')
        if server_data['ser_id'] in Server.objects.all().values_list('ser_id', flat=True):
            return Response({'error': '服务ID不能重复'}, status=status.HTTP_400_BAD_REQUEST)

        ser_serializer = self.get_serializer(data=server_data)

        self.valid(ser_serializer, seraddress_data_list)

        with transaction.atomic():
            server = ser_serializer.create(server_data)
            for adrs_data in seraddress_data_list:
                ip_data_info = adrs_data.pop('ser_ip')
                adrs_data['server'] = server
                adrs_serializer = SerAddressSerializer(data=adrs_data)
                adrs_instance = adrs_serializer.create(adrs_data)

                # 创建address下的所有ip
                ip_serializer = SerIpSerializer(data=ip_data_info, many=True)
                ip_create_list = ip_serializer.create(ip_data_info)
                # 为该address设置ip
                adrs_instance.ser_ip.set(ip_create_list)
        OperateLog.create_log(request)
        return Response(ServerSerializer(server).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        server_data = request.data
        seraddress_data_list = server_data.pop('ser_url')
        instance = self.get_object()
        if server_data['ser_id'] != instance.ser_id:
            if server_data['ser_id'] in Server.objects.all().values_list('ser_id', flat=True):
                return Response({'error': '服务ID不能重复'}, status=status.HTTP_400_BAD_REQUEST)

        ser_serializer = self.get_serializer(data=server_data)
        self.valid(ser_serializer, seraddress_data_list)

        with transaction.atomic():
            server = ser_serializer.update(instance, server_data)
            adrs_list = []

            for adrs_data in seraddress_data_list:
                ip_data_list = adrs_data.pop('ser_ip')
                adrs_data['server'] = server
                ip_list = []
                ip_creat_info = []
                if 'id' in adrs_data.keys():
                    adrs = SerAddress.objects.all().get(pk=adrs_data['id'])
                    adrs_serializer = SerAddressSerializer(data=adrs_data)
                    adrs_instance = adrs_serializer.update(adrs, adrs_data)

                    for ip_data in ip_data_list:
                        if 'id' in ip_data.keys():
                            ip = SerIp.objects.all().get(pk=ip_data['id'])
                            ip_serializer = SerIpSerializer(data=ip_data)
                            ip_serializer.update(ip, ip_data)
                            ip_list.append(ip)
                        else:
                            ip_creat_info.append(ip_data)

                else:
                    adrs_serializer = SerAddressSerializer(data=adrs_data)
                    adrs_instance = adrs_serializer.create(adrs_data)
                    for ip_data in ip_data_list:
                        ip_creat_info.append(ip_data)
                ip_creat_serializer = SerIpSerializer(data=ip_creat_info, many=True)
                ip_creat_list = ip_creat_serializer.create(ip_creat_info)
                ip_list.extend(ip_creat_list)
                adrs_instance.ser_ip.set(ip_list)

                adrs_list.append(adrs_instance)
            server.ser_url.set(adrs_list)
        OperateLog.create_log(request)
        return Response(ServerSerializer(server).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        ser_id = Server.objects.get(pk=pk).ser_id
        OpenStationViewSet.create_base_log(request, ser_id, "经典版服务", 2)
        return super(ServerViewSet, self).destroy(request, *args, **kwargs)


# 服务器类型
class SerTypeViewSet(viewsets.ModelViewSet):
    queryset = SerType.objects.all().order_by('-id')

    def get_serializer_class(self):
        if self.action == 'forgroup':
            return ForGroupSerTypeSerializer
        else:
            return SerTypeSerializer

    @list_route(methods=['get'])
    def forgroup(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(SerTypeViewSet, self).list(request, *args, **kwargs)

    @list_route(methods=['get'])
    def forserver(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(SerTypeViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(SerTypeViewSet, self).get_queryset()
        version_type = self.request.GET.get('version_type', None)
        if not version_type:
            version_type = CLASSIC_VERSION
        queryset = queryset.filter(version_type=version_type)
        return queryset.filter(version_type=version_type)

    def create(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        super(SerTypeViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(SerTypeViewSet, self).update(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': '修改关联信息失败', 'e': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        OperateLog.create_log(request)
        return super(SerTypeViewSet, self).destroy(request, *args, **kwargs)


# 服务组
class GroupViewSet(viewsets.ModelViewSet):
    queryset = ServerGroup.objects.all().order_by("-id")
    permission_classes = [ServerGroupsGroupPermission]

    def get_serializer_class(self):
        if self.suffix == 'List' and self.request.method == 'GET':
            return SimpGroupSerializer
        elif self.action == 'forgrid':
            return SimpGroupSerializer
        else:
            return GroupSerializer

    @list_route(methods=['get'])
    def forgrid(self, request, *args, **kwargs):
        self.pagination_class = None
        return super(GroupViewSet, self).list(request, *args, **kwargs)

    def get_queryset(self):
        # 服务组search
        queryset = ServerGroup.objects.all().order_by("-id")
        group_name = self.request.GET.get('group_name', "").strip()  # 服务组名称
        version_type = self.request.GET.get('version_type', None)
        if not version_type:
            version_type = CLASSIC_VERSION
        queryset = queryset.filter(version_type=version_type)
        if group_name:
            queryset = queryset.filter(group_name__icontains=group_name)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(GroupViewSet, self).create(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                super(GroupViewSet, self).update(request, *args, **kwargs)
                OperateLog.create_log(request)
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        kwargs = kwargs
        pk = kwargs.get("pk")
        group_name = ServerGroup.objects.get(pk=pk).group_name
        # 服务组删除记录
        OpenStationViewSet.create_base_log(request, group_name, "服务组", 2)
        return super(GroupViewSet, self).destroy(request, *args, **kwargs)


# 节点
class GridViewSet(viewsets.ModelViewSet):
    queryset = Grid.objects.all().order_by('-id')
    permission_classes = [GridGroupPermission]

    def get_serializer_class(self):
        if self.action == 'foropen':
            return SimpGridSerializer
        elif self.suffix == 'List' and self.request.method == 'GET':
            return SimpGridSerializer
        else:
            return GridSerializer

    @list_route(methods=['get'])
    def foropen(self, request, *args, **kwargs):
        self.pagination_class = None
        version_type = request.GET.get("version_type", "").strip()
        grid_query = Grid.objects.all()
        if version_type == '1':
            grid_query = grid_query.filter(version_type=1)
        elif version_type == '2':
            grid_query = grid_query.filter(version_type=2)
        serializer = self.get_serializer(grid_query, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Grid.objects.all().order_by('-id')
        grid_name = self.request.GET.get('grid_name', "").strip()  # 节点名称
        grid_site = self.request.GET.get('grid_site', "").strip()  # 机房
        deploy_way = self.request.GET.get('deploy_way', "").strip()  # 部署方式
        version_type = self.request.GET.get('version_type', "").strip()  # 服务分类
        is_open = self.request.GET.get('is_open', "").strip()  # 是否是开站
        if grid_name:
            queryset = queryset.filter(grid_name__icontains=grid_name)
        if grid_site:
            queryset = queryset.filter(grid_site=grid_site)
        if deploy_way:
            queryset = queryset.filter(deploy_way=deploy_way)
        if version_type:
            queryset = queryset.filter(version_type=version_type)
        if is_open:
            grid_ids = SerGrpInquriesViewSet.under_grid()
            queryset = queryset.filter(pk__in=grid_ids)
        return queryset

    def grid_valid(self, db_serializer, grid_serializer):

        db_serializer.is_valid(raise_exception=True)

        grid_serializer.is_valid(raise_exception=True)

    def get_related_id_list(self, gd_info):
        group_list = gd_info.pop('grp_list')
        grp_id_list = []
        for group in group_list:
            grp_id_list.append(group['group_id'])

        return grp_id_list

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        domain_name = data.get('domain_name')
        if domain_name:
            domain_name = eval(domain_name)
            data.update({"domain_name":domain_name})
            return Response(data)
        else:
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if request.data["version_type"] == 1:
            for db in request.data['database']:
                ret = mysql_test(host=db['db_address'], user=db['db_username'], password=db['db_pwd'],
                                 db=db['db_name'],
                                 port=db['db_port'])
                if not ret:
                    return Response({'error': '数据库配置录入数据错误，连接失败，请验证后重试'},
                                    status=status.HTTP_424_FAILED_DEPENDENCY)

            # 取数据库信息，验证数据库信息valid；取节点信息，验证节点数据valid
            del request.data['group']
            del request.data['db_info']
            grid_info = request.data
            databases_info = grid_info.pop('database')
            grid_info.pop('verinfo_list')

            grid_info.pop('verinfo_list')
            db_serializer = DataBaseInfoSerializer(data=databases_info, many=True)
            grid_serializer = SimpGridSerializer(data=grid_info)

            try:
                self.grid_valid(db_serializer, grid_serializer)
            except ValidationError as v:
                return Response({'error': str(v)}, status=status.HTTP_400_BAD_REQUEST)

            group_id_list = self.get_related_id_list(grid_info)

            # 创建节点对象, 创建数据库对象
            try:
                with transaction.atomic():
                    grid = grid_serializer.create(grid_info)
                    for db in databases_info:
                        db['grid'] = grid
                        db['db_pwd'] = encrypt(db['db_pwd'])
                        if 'dele' in db.keys():
                            del db['dele']

                    # 创建数据库对象
                    db = db_serializer.create(databases_info)
                    # 为该节点设置数据库
                    grid.db_info.set(db)
                    # 为该节点设置服务组
                    grid.group.set(ServerGroup.objects.all().filter(pk__in=group_id_list))
                    grid.save()
                    OperateLog.create_log(request)
                    return Response(GridSerializer(grid).data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif request.data["version_type"] == 2:#重构版节点新建
            version_type = 2
            grid_name = request.data["grid_name"]
            if Grid.objects.filter(grid_name=grid_name).exists():
                return Response({"error": "该节点已存在，不可重复"}, status=status.HTTP_400_BAD_REQUEST)
            grid_site = request.data["grid_site"]
            deploy_way = request.data["deploy_way"]
            domain_name = request.data["domain_name"]
            getFlashserver = request.data["getFlashserver"]
            visitors = request.data["visitors"]

            ref_grid_info={
                "version_type": version_type,
                "grid_name": grid_name,
                "grid_site": grid_site,
                "deploy_way": deploy_way,
                "domain_name": domain_name,
                "getFlashserver": getFlashserver,
                "visitors": visitors,
            }
            ret = Grid.objects.create(**ref_grid_info)
            return Response({"info": "重构版节点创建成功"}, status=status.HTTP_200_OK)
        return Response({"error": "请选择服务分类"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if request.data["version_type"] == 1:
            for db in request.data['database']:
                if ('id' in db.keys()) and (db['db_pwd'] == DataBaseInfo.objects.all().get(id=db['id']).db_pwd):
                    db['db_pwd'] = decrypt(db['db_pwd'])
                ret = mysql_test(host=db['db_address'], user=db['db_username'], password=db['db_pwd'],
                                 db=db['db_name'],
                                 port=db['db_port'])
                if not ret:
                    return Response({'error': '数据库配置录入数据错误，连接失败，请验证后重试'},
                                    status=status.HTTP_424_FAILED_DEPENDENCY)
            # 取数据库信息，验证数据库信息valid；取节点信息，验证节点数据valid
            del request.data['group']
            del request.data['db_info']
            grid_info = request.data
            databases_info = grid_info.pop('database')

            db_serializer = DataBaseInfoSerializer(data=databases_info, many=True)
            instance = self.get_object()
            grid_serializer = SimpGridSerializer(instance, data=grid_info)
            try:
                # 校验数据库信息和节点信息
                self.grid_valid(db_serializer, grid_serializer)
            except ValidationError as v:
                return Response({'error': str(v)}, status=status.HTTP_400_BAD_REQUEST)

            group_id_list = self.get_related_id_list(grid_info)

            # 创建节点对象, 创建数据库对象
            try:
                with transaction.atomic():
                    grid = grid_serializer.update(instance, grid_info)
                    db_list = []
                    db_create_info = []
                    for db in databases_info:
                        db['grid'] = grid
                        if 'dele' in db.keys():
                            del db['dele']
                        # 修改已存在的数据库信息
                        if 'id' in db.keys():
                            db_instance = DataBaseInfo.objects.filter(id=db['id'])
                            # 若密码修改，需将新密码加密后再入库
                            if db['db_pwd'] != db_instance.first().db_pwd:
                                db['db_pwd'] = encrypt(db['db_pwd'])

                            db_instance.update(**db)
                            # 将数据库对象添加至节点数据库列表中
                            db_list.append(db_instance.first())

                        else:  # 新增数据库，需将密码加密后再入库，将改数据库信息，放入新建数据库列表
                            db['db_pwd'] = encrypt(db['db_pwd'])
                            db_create_info.append(db)

                    # 创建新增数据库的serializer对象
                    db_create_serializer = DataBaseInfoSerializer(data=db_create_info, many=True)
                    # 创建新增数据库
                    db_create_list = db_create_serializer.create(db_create_info)
                    db_list.extend(db_create_list)

                    grid.db_info.set(db_list)
                    grid.group.set(ServerGroup.objects.all().filter(pk__in=group_id_list))
                    grid.save()
                    OperateLog.create_log(request)
                    return Response(GridSerializer(grid).data, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif request.data["version_type"] == 2:
            id = request.data["id"]
            version_type = 2
            grid_name = request.data["grid_name"]
            grid_site = request.data["grid_site"]
            deploy_way = request.data["deploy_way"]
            domain_name = request.data["domain_name"]
            getFlashserver = request.data["getFlashserver"]
            visitors = request.data["visitors"]
            ref_grid_info = {
                "version_type": version_type,
                "grid_name": grid_name,
                "grid_site": grid_site,
                "deploy_way": deploy_way,
                "domain_name": domain_name,
                "getFlashserver": getFlashserver,
                "visitors": visitors,
            }
            ret = Grid.objects.all().filter(pk=id).update(**ref_grid_info)
            return Response({"info": "重构版节点修改成功"}, status=status.HTTP_200_OK)
        return Response({"error": "请选择服务分类"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        kwargs = kwargs
        pk = kwargs.get("pk")
        grid_name = Grid.objects.get(pk=pk).grid_name
        # 删除记录
        OpenStationViewSet.create_base_log(request, grid_name, "节点", 2)
        return super(GridViewSet, self).destroy(request, *args, **kwargs)


# 数据库
class DataBaseInfoViewSet(viewsets.ModelViewSet):
    queryset = DataBaseInfo.objects.all().order_by('-id')
    serializer_class = DataBaseInfoSerializer


# @csrf_exempt
class SerAddressViewSet(viewsets.ModelViewSet):
    queryset = SerAddress.objects.all().order_by('-id')
    serializer_class = SerAddressSerializer

    @list_route(methods=['get'])
    def export(self, request, *args, **kwargs):
        version_type = int(self.request.GET.get('version_type', 0))
        if not version_type:
            return Response({'error': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)

        data = []

        first_grp = ServerGroup.objects.all().filter(version_type=version_type).first()
        if first_grp:
            ser_adrs_set = SerAddress.objects.all().filter(group=first_grp)

            serializer = SerAddressSerializer(ser_adrs_set, many=True)
            data = serializer.data

        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=server.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_prd = wb.add_sheet('server')

        style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x19;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """
                                    )
        style_body = xlwt.easyxf("""
                font:
                    name Arial,
                    bold off,
                    height 0XA0;
                align:
                    wrap on,
                    vert center,
                    horiz left;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """
                                 )

        # 1st line
        sheet_prd.write(0, 0, '服务ID', style_heading)
        sheet_prd.write(0, 1, '服务', style_heading)
        sheet_prd.write(0, 2, '地址名称', style_heading)
        sheet_prd.write(0, 3, 'IP', style_heading)
        sheet_prd.write(0, 4, 'IP', style_heading)
        sheet_prd.write(0, 5, 'IP', style_heading)
        sheet_prd.write(0, 6, 'IP', style_heading)

        row = 1
        for content in data:
            sheet_prd.write(row, 0, content['server'], style_body)
            sheet_prd.write(row, 1, content['ser_type'], style_body)
            sheet_prd.write(row, 2, content['ser_address'], style_body)
            n = 3
            for each in content['ser_ip']:
                sheet_prd.write(row, n, each['ser_ip'], style_body)
                n += 1

            # 第一行加宽
            sheet_prd.col(0).width = 100 * 50
            sheet_prd.col(1).width = 100 * 50
            sheet_prd.col(2).width = 400 * 50
            sheet_prd.col(3).width = 100 * 50
            sheet_prd.col(4).width = 100 * 50
            sheet_prd.col(5).width = 100 * 50
            sheet_prd.col(6).width = 100 * 50
            row += 1

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response

    def _excel_table_by_name(self, file_contents=None,
                             col_name_index=0, sheet_name=u'server'):
        """
            根据名称获取Excel表格中的数据
            参数: file_excel：Excel文件路径
                 col_name_index：表头列名所在行的索引
                 sheet_name：Sheet1名称
        """
        try:
            data = xlrd.open_workbook(file_contents=file_contents)
            table = data.sheet_by_name(sheet_name)
            n_rows = table.nrows  # 行数
            row_data = []
            for row_num in range(1, n_rows):
                row = table.row_values(row_num)
                row_data.append(row)
            return row_data
        except Exception as e:
            return False
    @list_route(methods=['post'])
    def import_save(self, request, *args, **kwargs):
        """
        author: gzh
        function: 经典版服务和重构版服务的导入功能
        param request: file 上传的导入文件
                       version_type  服务的类型：经典版-1；重构版-2；                    
        param args: None
        param kwargs: None
        return: 仅含状态码的Response
        """
        try:
            myFile = request.FILES["file"]  # 获取上传的文件，如果没有文件，则默认为None
            if not myFile:
                return Response({"error": "没有文件上传"}, status=status.HTTP_400_BAD_REQUEST)

            file = myFile.read()
            data = self._excel_table_by_name(file_contents=file)

            version_type = int(self.request.GET.get('version_type', 0))
            if not version_type:
                return Response({"error": "参数错误"}, status=status.HTTP_400_BAD_REQUEST)


            ser_dict = {}  # 将(server_id, ser_url)作key,value为对应的ip的列表
            num = 0
            url_set = set()  # 导入文件中的ser_url的集合
            ser_id_list = Server.objects.all().filter(version_type=version_type).values_list(
                'ser_id', 'id')
            ser_id_map = dict(ser_id_list)
            for adrs in data:
                """
                adrs[0] 服务ID
                adrs[1] 服务
                adrs[2] 地址名称
                adrs[3-6] ip
                逻辑：先改造数据结构，再创建服务，最后创建地址和IP
                """
                num += 1
                # 考虑 服务ID或服务未填的情况
                if not str(adrs[0]) and str(adrs[1]):
                    return Response({'error': '第{}行服务ID不能为空'.format(num)}, status=status.HTTP_400_BAD_REQUEST)
                elif not (str(adrs[0]) and str(adrs[1])):
                    continue

                ser_id = str(adrs[0]).strip()

                # 通过ser_id取server_id,用以新增服务地址
                if ser_id not in ser_id_map.keys():
                    return Response({'error': '服务ID{}不存在'.format(ser_id)}, status=status.HTTP_400_BAD_REQUEST)
                server_id = ser_id_map[ser_id]

                ser_url = str(adrs[2]).strip()
                url_set.add(ser_url)

                ser_dict.setdefault((server_id, ser_url), [])
                for num in range(3, 7):
                    if adrs[num]:
                        ser_dict[(server_id, ser_url)].append(str(adrs[num]).strip())

            address_serid_tuple = SerAddress.objects.all().values_list('server_id', 'ser_address')
            # 剔除掉已有的服务地址
            address_create_info = filter(lambda x: x not in address_serid_tuple, ser_dict.keys())

            # 新增服务地址
            address_create_list = []
            for address_info in address_create_info:
                server_id, ser_address = address_info
                address_create_list.append(SerAddress(server_id=server_id, ser_address=ser_address))

            SerAddress.objects.bulk_create(address_create_list)
            adrs_id_list = SerAddress.objects.all().filter(ser_address__in=url_set).values_list('server_id', "ser_address",
                                                                                                'id')
            adrs_id_map = map(lambda x: ((x[0], x[1]), x[2]), adrs_id_list)
            adrsid_list = map(lambda x: x[2], adrs_id_list)

            # 新增服务ip
            ip_create_info = set()
            for each in adrs_id_map:
                if each[0] in ser_dict.keys():
                    for ip in ser_dict[each[0]]:
                        ip_create_info.add((each[1], ip))
            ip_addr_tuple = SerIp.objects.all().filter(ser_address_id__in=adrsid_list).values_list('ser_address_id',
                                                                                                   'ser_ip')
            ip_create_info = filter(lambda x: x not in ip_addr_tuple, ip_create_info)

            ip_create_list = []
            for ip_info in ip_create_info:
                ip_create_list.append(SerIp(ser_address_id=ip_info[0], ser_ip=ip_info[1]))

            SerIp.objects.bulk_create(ip_create_list)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def deployway(request):
    fields = ['id', 'name']
    ret = {'data': []}
    for item in DEPLOY_WAYS:
        ret['data'].append(dict(zip(fields, item)))
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def cli_version(request):
    fields = ['id', 'name']
    ret = {'data': []}
    for item in CLI_CHOICES:
        ret['data'].append(dict(zip(fields, item)))
    return Response(ret, status=status.HTTP_200_OK)


@api_view(['GET'])
def deploy_way_grid_ship(request):
    ships = Grid.objects.all().values_list("grid_name", "id", "deploy_way")
    deploy_ways_map = dict(DEPLOY_WAYS)
    data = {}
    for grid_name, grid_id, deploy_way in ships:
        deploy_way = deploy_ways_map[deploy_way]
        data.setdefault(deploy_way, [])
        data[deploy_way].append({
            "id": grid_id,
            "name": grid_name
        })
    all_deploy_way = deploy_ways_map.values()
    for d_w in all_deploy_way:
        if d_w not in data.keys():
            data[d_w] = []
    return Response([{"name": k, "children": v} for k, v in data.items()])


@api_view(['GET'])
def deploy_way_group_ship(request):
    grid_set = Grid.objects.all()
    deploy_way_map = dict(DEPLOY_WAYS)

    grid_serializer = ForShipGridSerializer(grid_set, many=True)
    grid_data = grid_serializer.data
    data = {}
    for each in grid_data:

        group_list = []
        deploy_way = each['deploy_way']
        for group in each['group']:
            group_id, group_name, _ = group.values()
            group_list.append({'id': group_id, 'name': group_name})

        data.setdefault(deploy_way, [])

        data[deploy_way].append(
            {
                "id": each['id'],
                "name": each['grid_name'],
                "children": group_list
            })
    for dep_way in deploy_way_map.keys():
        if dep_way not in data.keys():
            data[dep_way] = []

    return Response([{"id": key, "name": deploy_way_map[key], "children": value} for key, value in data.items()],
                    status=status.HTTP_200_OK)


@api_view(['GET'])
def version_type(request):
    data = [{"id": i[0], "name": i[1]} for i in PROD_SERV_VERSIONS]
    # data = [dict(zip(("id", "name"), i)) for i in PROD_SERV_VERSIONS]
    return Response(data)


@csrf_exempt
def function_selection_import(request):
    if not request.method == "POST":
        return JsonResponse({"error": "method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    product_id = int(request.GET.get("product", 0))
    if not product_id:
        return JsonResponse({"error": "parameter error"}, status=status.HTTP_400_BAD_REQUEST)

    excel = xlrd.open_workbook(file_contents=request.FILES["file"].read())
    table = excel.sheets()[0]
    if table.nrows < 2 or (table.row_values(1) != ['功能名称', '功能路径', '功能类型', '客户版本', '选项名称', '选项值', '是否默认']):
        return JsonResponse({"error": "The format of the imported file is wrong."}, status=status.HTTP_400_BAD_REQUEST)

    for num in range(2, table.nrows):
        func_code, func_name, func_type, cli_ver, slc_name, slc_val, is_default = table.row_values(num)

        function_obj, _ = FunctionInfo.objects.update_or_create(
            defaults=dict(func_name=func_name, cli_version=cli_ver, func_type=func_type),
            func_code=func_code, product_id=product_id)
        if func_type == '单选框':
            SingleSelection.objects.update_or_create(
                defaults=dict(select_value=slc_val, is_default=bool(int(is_default))),
                function=function_obj, select_name=slc_name, )

    return JsonResponse({"msg": "import success"})


@api_view(['POST'])
def auto_group_grid(request):
    """
    生态云-经典版服务&服务组&节点自动新增接口
    :param request:
    :return:
    """
    datas = request.data
    dep_dict = dict(DEPLOY_WAYS)
    deploy_dict = {v: k for k, v in dep_dict.items()}

    # 遍历数据获取单个节点相关的所有数据
    for key, values in datas.items():
        with transaction.atomic():
            version_type = values.get("version_type")
            #经典版服务相关的数据
            server = values.get("server")
            for ser in server:
                ser_id = ser.get("ser_id")
                ser_name = ser.get("ser_name")
                ser_addresl = ser.get("ser_addresl")

                ser_id_exists = Server.objects.filter(ser_id=ser_id).exists()
                if ser_id_exists == True:
                    return Response({"error": ser_id+"服务ID已存在"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    ser_type = SerType.objects.get(ser_type=ser_name)
                except:
                    return Response({"error": ser_name+"服务类型不存在"}, status=status.HTTP_400_BAD_REQUEST)

                server = Server.objects.create(ser_id=ser_id, version_type=version_type)
                server.ser_name = ser_type
                server.save()
                print(f"经典版服务{ser_id}和{ser_name}服务类型新增完成" )

                # 新增服务地址
                for ser_add in ser_addresl:
                    address = SerAddress.objects.create(ser_address=ser_add)
                    address.server = server
                    address.save()
                    print(f"{ser_id}经典版服务的{ser_add}地址新增完成")

            # 获取服务组相关信息
            ser_group = values.get("ser_group")
            for group in ser_group:
                serid_list = group.get("serid_list")
                group_name = group.get("group_name")

                group_exist = ServerGroup.objects.all().filter(group_name=group_name).exists()
                if group_exist == True:
                    return Response({"error": group_name + "服务组已存在"}, status=status.HTTP_400_BAD_REQUEST)

                group_create = ServerGroup.objects.create(group_name=group_name, version_type=version_type)
                print(f"经典版服务组{group_name}新增完成")
                for add_g in serid_list:
                    add_exists = SerAddress.objects.all().filter(ser_address=add_g).exists()
                    if not add_exists:
                        return Response({"error": add_g + "服务地址不存在"}, status=status.HTTP_400_BAD_REQUEST)
                    group_add = SerAddress.objects.all().filter(ser_address=add_g).order_by('-id').first()
                    group_create.ser_address.add(group_add)
                    group_create.save()
                    print(f"经典版服务组{group_name}的{add_g}服务地址新增完成")


            # 获取节点相关信息
            grid_name = key
            grid_info = values.get("grid")

            database = grid_info.get("database")
            # 验证数据库是否可连接
            for dbs in database:
                ret = mysql_test(host=dbs['db_address'], user=dbs['db_username'], password=dbs['db_pwd'],
                                 db=dbs['db_name'],
                                 port=dbs['db_port'])
                if not ret:
                    return Response({'error': f'{db}数据库配置录入数据错误，连接失败，请验证后重试'},
                                    status=status.HTTP_424_FAILED_DEPENDENCY)

            deploy_way = grid_info.get("deploy_way")
            grid_site = grid_info.get("grid_site")

            grp_list = grid_info.get("grp_list")
            grid_dict = {
                "grid_name": grid_name,
                "grid_site": grid_site,
                "version_type": version_type,
                "deploy_way": deploy_dict[deploy_way],
            }

            grid_exits = Grid.objects.all().filter(grid_name=grid_name).exists()

            if grid_exits == True:
                return Response({"error": grid_name + "节点已存在"}, status=status.HTTP_400_BAD_REQUEST)
            grid_create = Grid.objects.create(**grid_dict)

            for dbiterm in database:
                db_dict = {
                    "db_type": dbiterm["db_type"],
                    "db_address": dbiterm["db_address"],
                    "db_name": dbiterm["db_name"],
                    "db_username": dbiterm["db_username"],
                    "db_pwd": encrypt(dbiterm["db_pwd"]),
                    "db_port": dbiterm["db_port"],
                    "grid": grid_create,
                }
                db_name = dbiterm["db_name"]
                db_create = DataBaseInfo.objects.create(**db_dict)
                print(f"{db_name}数据库新增成功")


            grid_create.group.set(ServerGroup.objects.all().filter(group_name__in=grp_list))
            grid_create.save()
            print(f"{key}节点新增成功")

    return Response(data={"info": "ojbk"}, status=status.HTTP_200_OK)


