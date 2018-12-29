import datetime

from django.db.models import Sum, Min
from rest_framework import serializers

from applications.data_manage.models import InquiriesData, OnlineClientData, \
    OnlineProductData
from applications.workorder_manage.models import OpenStationManage
from ldap_server.configs import DEPLOY_WAYS, CHANNEL_UNKNOWN, CHANNEL_PC, CHANNEL_WECHAT,\
    CHANNEL_APP, CHANNEL_WAP, CHANNEL_IOS, CHANNEL_ANDROID, CHANNEL_WEIBO, CHANNEL_QQ


class PandectDataSerializer(serializers.ModelSerializer):
    """
    总览页面的serializer
    """
    company_id = serializers.CharField(source='station_info.company_id', read_only=True)
    company_name = serializers.CharField(source='company_info.company_name', read_only=True)
    open_station_time = serializers.DateField(source='station_info.open_station_time', read_only=True)
    close_station_time = serializers.DateField(source='station_info.close_station_time', read_only=True)
    industry = serializers.CharField(source='company_info.industry.industry', read_only=True)
    grid = serializers.CharField(source='station_info.grid.grid_name', read_only=True)
    server_grp = serializers.CharField(source='station_info.server_grp.group_name', read_only=True)

    def get_deploy_way(self, data):
        """
        author:gzh
        function:获取某站点部署方式
        param data:某OpenStationManage对象的数据
        return: 部署方式的代码
        """
        obj = dict(DEPLOY_WAYS)[data.station_info.deploy_way]
        if obj:
            return obj
        return None

    def get_inquiries_data(self, data):
        """
        author:gzh
        function:获取某站点各渠道的咨询量
        param data: 某OpenStationManage对象的数据
        return: 各渠道的咨询量
        """
        channel_set = data.inquiries_data.values('channel').annotate(value=Sum('inquires_num')). \
            values_list('channel', 'value')
        return dict(channel_set)

    def get_start_date(self, data):
        """
        author:gzh
        function:获取某站点开站的日期
        param data: 某OpenStationManage对象的数据
        return: 开站日期
        """
        ret = data.inquiries_data.aggregate(start_date=Min('date'))
        return ret['start_date']

    start_date = serializers.SerializerMethodField()
    inquiries_data = serializers.SerializerMethodField()
    deploy_way = serializers.SerializerMethodField()

    class Meta:
        model = OpenStationManage
        fields = ('id', 'company_id', 'company_name', 'open_station_time', 'close_station_time', 'industry', \
                  'deploy_way', 'grid', 'server_grp', 'inquiries_data', 'start_date')


class OnlineClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineClientData
        fields = '__all__'


class InquiriesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiriesData
        fields = '__all__'


class OnlineProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineProductData
        fields = ('id', 'online_num', 'product_id', 'deploy_way', 'industry', 'date')


class GridInquiresSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiriesData

