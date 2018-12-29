import logging
import json

from django.db import transaction
from rest_framework import serializers

from applications.production_manage.models import Grid, Product, SingleSelection, FunctionInfo
from applications.production_manage.serializers import SingleSelectionSerializer, ForDependSelectionSerializer, \
    ForOpenSelectionSerializer
from applications.workorder_manage.models import CompanyUrl, AreaInfo, CompanyAddress, Industry, ContactInfo, \
    AccountConf, OpenStationManage, CompanyInfo, StationInfo, OrderManage, Matter, Reject, Attachment

log = logging.getLogger("Django")


# 公司网址 单行文本框 company_url 数组
class CompanyUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUrl
        fields = ('id', 'company_url')


class AreaInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaInfo
        fields = ('id', 'atitle', 'aPArea')


class CompanyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAddress
        fields = ('id', 'province', 'city', 'detail')


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'industry')


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ('id', 'linkman', 'link_phone', 'link_email', 'link_qq', 'link_type', 'link_work')


class AccountConfSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountConf
        fields = ('id', 'user_name', 'set_pwd')


class SimpCompanyInfoSerializer(serializers.ModelSerializer):
    # 【外键】 所属行业 下拉列表框 industry 字符串 必填 外键
    industry = serializers.SlugRelatedField(
        read_only=True,
        slug_field='industry'
    )

    class Meta:
        model = CompanyInfo
        fields = ('id', 'station_type', 'industry', 'company_name')


class OrderManageSerializer(serializers.ModelSerializer):
    """
    订单序列化
    """
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    cashed_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = OrderManage
        # fields = '__all__'
        fields = ("id", "contract_start_time", "contract_end_time", "contract_index", "contract_accessory",
                  "contract_amount", "amount_cashed", "cashed_time", "created_at", "contract_content")

class KHKCompanyInfoSerializer(serializers.ModelSerializer):
    """
    客户库使用序列化
    """
    # 【外键】公司网址 单行文本框 company_url 数组
    company_url = CompanyUrlSerializer(many=True, read_only=True)

    # 【外键】公司地址 下拉列表框 单行文本框 company_address 对象 256 / 必填
    company_address = CompanyAddressSerializer(read_only=True)
    # 【外键】 所属行业 下拉列表框 industry 字符串 必填 外键
    industry = serializers.SlugRelatedField(
        read_only=True,
        slug_field='industry'
    )
    # 订单信息
    order_info = OrderManageSerializer(read_only=True)
    # 【外键】 联系人信息：点击增加联系人 联系电话 电子邮箱和QQ号文本；最多增加三个联系人；增加的文本均必填。
    link_info = ContactInfoSerializer(many=True, read_only=True)

    class Meta:
        model = CompanyInfo
        fields = ('id', 'station_type', 'company_name', 'abbreviation', 'company_url', 'company_address',
                  'industry', 'company_email', 'GSZZ', 'customer_type', 'service_area', 'visitor',
                  'consult', 'brand_effect', 'customer_level', 'platform_informatiom', 'training_method',
                  'special_selection', 'sign_contract', 'kf_number', 'order_info', 'comment',
                  'transmitting_state', 'cli_version', 'link_info', 'classify', 'deploy_way')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                company = super(KHKCompanyInfoSerializer, self).create(validated_data)
                # 公司网址
                company_url_list = self.initial_data.get('company_url')
                print('======', company_url_list)
                if company_url_list:
                    for url in company_url_list:
                        com_url = CompanyUrl.objects.create(company_url=url['company_url'], company_info=company)
                        com_url.save()

                # 公司地址
                company_address = self.initial_data.get('company_address')
                if company_address:
                    province = AreaInfo.objects.all().get(pk=company_address['province'])
                    city = AreaInfo.objects.all().get(pk=company_address['city'])
                    company.company_address = CompanyAddress.objects.all().create(province=province, city=city,
                                                                                  detail=company_address['detail'])

                # 订单信息
                order_info = self.initial_data.get('order_info')
                if order_info:
                    accessory = order_info.get('contract_accessory')

                    contract_content = str(order_info.get('contract_content'))
                    company.order_info = OrderManage.objects.all().create(
                        contract_start_time=order_info['contract_start_time'],
                        contract_end_time=order_info['contract_end_time'],
                        contract_index=order_info['contract_index'],
                        contract_accessory=accessory,
                        contract_amount=order_info.get('contract_amount'),
                        amount_cashed=order_info.get('amount_cashed'),
                        cashed_time=order_info.get('cashed_time'),
                        contract_content=str(contract_content))

                # 行业
                industry = self.initial_data.get('industry')
                if industry:
                    company.industry = Industry.objects.all().get(industry=industry)

                # 联系人信息
                link_info_list = self.initial_data.get('link_info')
                for link_info in link_info_list:
                    if link_info:
                        ContactInfo.objects.create(company=company, **link_info)

                company.save()
                return company
        except Exception as e:
            log.error(e)
            raise TypeError(e)


class KHKCSCSerializer(serializers.ModelSerializer):
    """
    客户库CSC审核使用页面序列化
    """
    order_info = serializers.SlugRelatedField(
        read_only=True,
        slug_field='created_at'
    )
    industry = serializers.SlugRelatedField(
        read_only=True,
        slug_field='industry'
    )

    class Meta:
        model = CompanyInfo
        fields = ('id', 'industry', 'company_name', 'cli_version', 'order_info', 'deploy_way')


class KHKSmallCompanyInfoSerializer(serializers.ModelSerializer):
    """
    客户库销售使用页面序列化
    """
    class Meta:
        model = CompanyInfo
        fields = ('id', 'transmitting_state', 'company_name', 'cli_version', 'comment')


class CompanyInfoSerializer(serializers.ModelSerializer):
    # 【外键】公司网址 单行文本框 company_url 数组
    company_url = CompanyUrlSerializer(many=True, read_only=True)

    # 【外键】公司地址 下拉列表框 单行文本框 company_address 对象 256 / 必填
    company_address = CompanyAddressSerializer(read_only=True)

    # 【外键】 所属行业 下拉列表框 industry 字符串 必填 外键
    industry = serializers.SlugRelatedField(
        read_only=True,
        slug_field='industry'
    )

    class Meta:
        model = CompanyInfo
        fields = (
            'id', 'station_type', 'company_name', 'abbreviation', 'company_url', 'company_address',
            'industry', 'company_email', 'GSZZ', 'customer_type', 'service_area', 'cli_version',
            'deploy_way', 'classify')


class SimpStationInfoSerializer(serializers.ModelSerializer):
    # 节点选择 下拉列表框 grid 对象 必填 数据来源已创建的节点；选择部署方式后才可选择节点
    grid = serializers.SlugRelatedField(
        read_only=True,
        slug_field='grid_name'
    )

    def get_classify_name(self, data):
        return data.classsify_name

    classify_name = serializers.SerializerMethodField()

    class Meta:
        model = StationInfo
        fields = (
            'id', 'company_id', 'grid', 'classify_name', 'deploy_way', 'cli_version', 'open_station_time',
            'close_station_time', 'order_work', 'version_id')


class StationInfoSerializer(serializers.ModelSerializer):
    # 节点选择 下拉列表框 grid 对象 必填 数据来源已创建的节点；选择部署方式后才可选择节点
    # grid = serializers.SlugRelatedField(
    #     read_only=True,
    #     slug_field='grid_name'
    # )

    # 合同产品 复选按钮 pact_products 列表 必填 数据来源于已创建的产品
    # pact_products = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='product'
    # )

    class Meta:
        model = StationInfo
        fields = (
            'id', 'company_id', 'deploy_way', 'validity_days', 'grid', 'classify', 'cli_version', 'pact_products',
            'open_station_time', 'version_id',
            'close_station_time', 'sales', 'pre_sales', 'oper_cslt', 'impl_cslt', 'oper_supt',
            'order_work')


class SimpOpenStationManageSerializer(serializers.ModelSerializer):
    company_info = SimpCompanyInfoSerializer(read_only=True)
    station_info = SimpStationInfoSerializer(read_only=True)

    class Meta:
        model = OpenStationManage
        fields = ('id', 'online_status', 'company_info', 'station_info')


class CustomerOpenStationManageSerializer(serializers.ModelSerializer):
    """
    企业信息
    """
    company_info = CompanyInfoSerializer(read_only=True)
    """
    站点信息
    """
    station_info = StationInfoSerializer(read_only=True)
    class Meta:
        model = OpenStationManage
        fields = (
            'id','company_info','station_info'
        )


class OpenStationManageSerializer(serializers.ModelSerializer):
    """
    企业信息
    """
    company_info = CompanyInfoSerializer(read_only=True)

    # 【外键】 联系人信息：点击增加联系人 联系电话 电子邮箱和QQ号文本；最多增加三个联系人；增加的文本均必填。
    link_info = ContactInfoSerializer(many=True, read_only=True)

    """
    站点信息
    """
    station_info = StationInfoSerializer(read_only=True)

    # func_list 选项 单行文本框、下拉列表框 selections 对象 选填 数据来源于功能开关带动的文本类型
    # 具体到节点和版本 请求product/version/
    func_list = ForOpenSelectionSerializer(many=True, read_only=True)

    # 【外键】 账户配置信息 account_conf
    account_conf = AccountConfSerializer(many=True, read_only=True)

    class Meta:
        model = OpenStationManage
        fields = (
            'id', 'online_status', 'company_info', 'func_list', 'account_conf', 'station_info', 'link_info')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                station = super(OpenStationManageSerializer, self).create(validated_data)

                """
                公司信息
                """
                company_url_list = self.initial_data['company_info'].pop('company_url')
                company_address = self.initial_data['company_info'].pop('company_address')
                industry = self.initial_data['company_info'].pop('industry')

                cmp_data = self.initial_data['company_info']
                company_info = CompanyInfo.objects.create(open_station=station, **cmp_data)
                company_info.open_station = station

                # compcany_url
                for url in company_url_list:
                    com_url = CompanyUrl.objects.create(company_url=url['company_url'], company_info=company_info)
                    com_url.company_info = company_info
                    com_url.save()

                # company_address
                province = AreaInfo.objects.all().get(pk=company_address['province'])
                city = AreaInfo.objects.all().get(pk=company_address['city'])
                com_ad = CompanyAddress.objects.all().create(company_info=company_info, province=province, city=city,
                                                             detail=company_address['detail'])
                com_ad.company_info = company_info
                com_ad.save()

                # industry
                company_info.industry = Industry.objects.all().get(industry=industry)

                company_info.cli_version = int(self.initial_data['station_info']["classify"])

                company_info.save()

                """
                联系人信息
                """
                # link_info
                link_info_list = self.initial_data['link_info']
                for link_info in link_info_list:
                    ContactInfo.objects.create(station=station, **link_info, company=company_info)

                """
                站点信息
                """
                grid = self.initial_data['station_info'].pop('grid')
                pact_products_list = self.initial_data['station_info'].pop('pact_products')

                sta_data = self.initial_data['station_info']
                sta_data['classify'] = int(sta_data['classify'])
                station_info = StationInfo.objects.create(open_station=station, **sta_data)
                station_info.open_station = station

                # grid
                station_info.grid = Grid.objects.all().get(id=grid)

                # pact_products
                for product in pact_products_list:
                    station_info.pact_products.add(Product.objects.all().get(id=product))
                station_info.save()

                """
                功能开关表信息
                """
                # func_list
                prod_selc_list = self.initial_data['func_list']
                for prod_selc in prod_selc_list:
                    for selc in prod_selc['id']:
                        station.func_list.add(SingleSelection.objects.all().get(pk=selc))
                    for txt in prod_selc['ipu']:
                        func = FunctionInfo.objects.all().get(pk=txt['id'])
                        text = SingleSelection.objects.create(function=func, select_name=txt['value'],
                                                              select_value=txt['value'])
                        text.save()
                        station.func_list.add(text)


                """
                账户配置信息
                """
                # account_conf
                account_conf_list = self.initial_data['account_conf']
                for account_conf in account_conf_list:
                    if "sure_pwd" in account_conf:
                        account_conf.pop("sure_pwd")
                    AccountConf.objects.create(station=station, **account_conf)

                station.save()
                return station
        except Exception as e:
            log.error(e)
            raise TypeError(e)


class NewStationManageSerializer(serializers.ModelSerializer):
    company_info = SimpCompanyInfoSerializer(read_only=True)
    station_info = SimpStationInfoSerializer(read_only=True)

    class Meta:
        model = OpenStationManage
        fields = ('id', 'company_info', 'station_info', 'online_status')


class RejectSerializer(serializers.ModelSerializer):
    """培训驳回原因"""
    class Meta:
        model = Reject
        fields = ('id', 'dismiss_reason')


class AttachmentSerializer(serializers.ModelSerializer):
    """培训附件上传"""
    class Meta:
        model = Attachment
        fields = ('id', 'enclosure')


class MatterSerializer(serializers.ModelSerializer):

    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    start_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    end_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = Matter
        fields = ("id", "created_at", "updated_at", "matter_type", "matter_status", "training_method", "legacy_issue", "satisfaction_level",
                  "communication_way", "final_training_method", "matter_name", "training_contactnum", "training_contactqq",
                  "training_position", "invest_start", "invest_end", "start_time", "end_time", "description_customer", "online_module",
                  "untrained_cause", "termination_reason", "customer_training_needs", "training_model", "problem_description",
                  "customer_feedback", "responsible", "training_instructors", "dealing_person", "investigador", "training_contact",
                  "company_matter")