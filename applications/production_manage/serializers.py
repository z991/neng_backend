import logging

from rest_framework import serializers
from applications.version_manage.models import VersionProduct
from applications.production_manage.models import Product, SingleSelection, FunctionInfo, VersionInfo, \
    SerIp, Server, SerType, SerAddress, ServerGroup, DataBaseInfo, Grid

log = logging.getLogger('django')


class SingleSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleSelection
        fields = ('id', 'select_name', 'select_value', 'is_default')


class ForDetailSelectionSerializer(serializers.ModelSerializer):
    func_type = serializers.CharField(source='function.func_type', read_only=True)

    class Meta:
        model = SingleSelection
        fields = ('id', 'select_name', 'select_value', 'function', 'func_type')


class ForParentFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionInfo
        fields = ('id', 'func_name', 'parent')


class ForDependSelectionSerializer(serializers.ModelSerializer):
    function = ForParentFunctionSerializer(read_only=True)

    class Meta:
        model = SingleSelection
        fields = ('id', 'function', 'select_name', 'select_value')


class ForOpenSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleSelection
        fields = ('id', 'function', 'select_name', 'select_value')


class SimpFuncInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionInfo
        fields = ('id', 'func_name', 'cli_version', 'func_code', 'func_type')


class FunctionInfoSerializer(serializers.ModelSerializer):
    selection = SingleSelectionSerializer(many=True, read_only=True)

    class Meta:
        model = FunctionInfo
        fields = (
            'id', 'product', 'func_name', 'cli_version', 'func_code', 'func_type', 'selection')
        read_only_fields = ("product",)

    def create(self, validated_data):
        instance = FunctionInfo.objects.create(**validated_data)
        instance.product_id = self.initial_data['product']
        return instance

    def update(self, instance, validated_data):
        instance = super(FunctionInfoSerializer, self).update(instance, validated_data)
        instance.product_id = self.initial_data['product']
        return instance


class NewFunctionInfoSerializer(serializers.ModelSerializer):
    selection = SingleSelectionSerializer(many=True, read_only=True)

    class Meta:
        model = FunctionInfo
        fields = (
            'id', 'func_name', 'selection')


class ForDetailFunctionSerializer(serializers.ModelSerializer):
    dependences = ForDetailSelectionSerializer(many=True, read_only=True)
    parent = ForDetailSelectionSerializer(many=True, read_only=True)
    selection = SingleSelectionSerializer(many=True, read_only=True)

    class Meta:
        model = FunctionInfo
        fields = (
            'id', 'product', 'func_name', 'cli_version', 'func_code', 'func_type', 'selection', 'dependences',
            'parent')
        read_only_fields = ("product", 'dependences', 'parent')


class ForOpenFunctionSerializer(serializers.ModelSerializer):
    parent = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='function_id',
    )
    selection = SingleSelectionSerializer(many=True, read_only=True)

    class Meta:
        model = FunctionInfo
        fields = (
            'id', 'func_name', 'func_type', 'parent', 'selection')


class VersionInfoSerializer(serializers.ModelSerializer):
    function = FunctionInfoSerializer(many=True, read_only=True)
    product = serializers.CharField(source="product.product", read_only=True)

    class Meta:
        model = VersionInfo
        fields = ('id', 'product', 'pro_version', 'function')

    def create(self, validated_data):
        instance = VersionInfo.objects.create(**validated_data)
        instance.product_id = self.initial_data['product']
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.pro_version = validated_data.get('pro_version', instance.pro_version)
        instance.product_id = self.initial_data['product']
        instance.save()
        return instance


class SimpVersionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionInfo
        fields = ('id', 'pro_version')


class ForGridVersionInfoSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.product", read_only=True)

    class Meta:
        model = VersionInfo
        fields = ('id', 'pro_version', 'product')


class ComplexVersionSerializer(serializers.ModelSerializer):
    function = FunctionInfoSerializer(many=True, read_only=True)

    class Meta:
        model = VersionInfo
        fields = ('id', 'pro_version', 'function')


class ForDateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'product')


class SimpProductSerializer(serializers.ModelSerializer):
    def get_version_count(self, product):
        count = VersionInfo.objects.all().filter(product=product).count()
        return count

    version_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'product', 'version_count')


class VersionProductSerializer(serializers.ModelSerializer):
    def get_version_count(self, product):
        count = VersionInfo.objects.all().filter(product=product).count()
        return count

    version_count = serializers.SerializerMethodField()

    def get_version(self, product):
        version = VersionProduct.objects.all().filter(product_name=product.product)\
            .values_list('product_version', 'release_status', 'release_date')
        init_version = ''
        if version:
            init_date = ''
            for item_version, status, date_time in version:
                if status:
                    if init_date:
                        if date_time>init_date:
                            init_version = item_version
                    else:
                        init_date = date_time
                        init_version = item_version
            return init_version
        return ''

    version = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'product', 'version_count', 'version')


class ProductSerializer(serializers.ModelSerializer):
    version = SimpVersionInfoSerializer(many=True, read_only=True)
    function = SimpFuncInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'product', 'classify', 'version', 'function')


class ForOpenProductSerializer(serializers.ModelSerializer):
    function = ForOpenFunctionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'function', 'product')


class SerIpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SerIp
        fields = ('id', 'ser_ip')


class SimpSerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SerAddress
        fields = ('id', 'ser_address')


class SerAddressSerializer(serializers.ModelSerializer):
    ser_ip = SerIpSerializer(many=True, read_only=True)
    server = serializers.CharField(source='server.ser_id', read_only=True)
    ser_type = serializers.CharField(source='server.ser_name.ser_type', read_only=True)

    class Meta:
        model = SerAddress
        fields = ('id', 'ser_address', 'ser_ip', 'server', 'ser_type')


class SimpServerSerializer(serializers.ModelSerializer):
    ser_url = SimpSerAddressSerializer(many=True)

    class Meta:
        model = Server
        fields = ('id', 'ser_id', 'ser_url')


class ServerSerializer(serializers.ModelSerializer):
    ser_url = SerAddressSerializer(many=True, read_only=True)

    class Meta:
        model = Server
        fields = ('id', 'ser_id', 'ser_name', 'ser_url', 'version_type')

    # 重写post请求的方法
    def create(self, validated_data):
        server = Server()
        server.ser_id = validated_data['ser_id']
        server.version_type = validated_data['version_type']
        server.ser_name = SerType.objects.all().get(pk=validated_data['ser_name'])
        server.save()
        return server

    # 重写put请求的方法
    def update(self, instance, validated_data):
        instance.ser_id = validated_data.get('ser_id', instance.ser_id)
        instance.version_type = validated_data['version_type']
        instance.ser_name = SerType.objects.all().get(pk=validated_data['ser_name'])
        instance.save()
        return instance


class SerTypeSerializer(serializers.ModelSerializer):
    cor_product = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field='product',
        queryset=Product.objects.all()
    )

    class Meta:
        model = SerType
        fields = ('id', 'ser_type', 'cor_product', 'version_type')

    def update(self, instance, validated_data):
        validated_data.pop('cor_product')
        product_data = self.initial_data['pro_list']
        super(SerTypeSerializer, self).update(instance, validated_data)

        instance.cor_product.clear()
        for item in product_data:
            instance.cor_product.add(Product.objects.all().get(product=item))
        instance.save()
        return instance


class ForGroupSerTypeSerializer(serializers.ModelSerializer):
    server = SimpServerSerializer(many=True, read_only=True)

    class Meta:
        model = SerType
        fields = ('id', 'ser_type', 'server')


class SimpGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerGroup
        fields = ('id', 'group_name', 'version_type')


class GroupSerializer(serializers.ModelSerializer):
    ser_address = SerAddressSerializer(many=True)

    class Meta:
        model = ServerGroup
        fields = ('id', 'group_name', 'grid', 'ser_address', 'version_type')

    # 重写post请求的方法
    def create(self, validated_data):
        # 新建group,无server信息
        del validated_data['ser_address']
        addr_list = self.initial_data['addr_list']
        group = super(GroupSerializer, self).create(validated_data)
        # 插入ser_address
        for item in addr_list:
            # if not item['id']:
            #     continue
            group.ser_address.add(SerAddress.objects.all().filter(pk=item['id']).first())
        group.save()
        return group

    # 重写put请求的方法
    def update(self, instance, validated_data):
        # 忽略server信息，update本group,
        del validated_data['ser_address']
        addr_list = self.initial_data['addr_list']

        super(GroupSerializer, self).update(instance, validated_data)

        # 清空本group中的server信息，插入新的server
        instance.ser_address.clear()
        for item in addr_list:
            instance.ser_address.add(SerAddress.objects.all().filter(pk=item['id']).first())
        instance.save()
        return instance


class DataBaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataBaseInfo
        fields = ('id', 'db_type', 'db_address', 'db_name', 'db_username', 'db_pwd', 'db_port')


class SimpGridSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grid
        fields = ('id', 'grid_name', 'grid_site', 'deploy_way', 'version_type', 'domain_name', 'getFlashserver', "visitors")


class ForShipGridSerializer(serializers.ModelSerializer):
    group = SimpGroupSerializer(many=True)

    class Meta:
        model = Grid
        fields = ('id', 'grid_name', 'deploy_way', 'group')


class GridSerializer(serializers.ModelSerializer):
    group = SimpGroupSerializer(many=True)
    db_info = DataBaseInfoSerializer(many=True)

    def get_products(self, grid):

        try:
            products = Product.objects.all().filter(version__grid=grid).values('id', 'product')
            return products

        except Exception as e:
            log.error(e)
            return None

    products = serializers.SerializerMethodField()

    class Meta:
        model = Grid
        fields = (
            'id', 'grid_name', 'grid_site', 'deploy_way', 'group', 'products', 'db_info',
            'version_type', "domain_name", "getFlashserver", "visitors")

    def update(self, instance, validated_data):
        instance.grid_name = validated_data.get('grid_name', instance.grid_name)  # 节点名
        instance.grid_site = validated_data.get('grid_site', instance.grid_site)  # 机房
        instance.deploy_way = validated_data.get('deploy_way', instance.deploy_way)
        instance.save()
        return instance
