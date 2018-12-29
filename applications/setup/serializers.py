import logging

from rest_framework import serializers
from applications.workorder_manage.models import Industry
from applications.setup.models import SiteReceptionGroup
from applications.workorder_manage.models import StationInfo


log = logging.getLogger("Django")


class CliIndustrySerializer(serializers.ModelSerializer):
    def get_site_num(self, data):
        site_num = data.company_info.count()
        return site_num

    site_num = serializers.SerializerMethodField()

    class Meta:
        model = Industry
        fields = ('id', 'industry', 'site_num')


# 公司企业id
class CompanyIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationInfo
        fields = ("company_id", )


class SiteReceptionGroupSerializer(serializers.ModelSerializer):
    """接待组站点序列化器"""
    # set_info = serializers.ListField(child=serializers.SlugField())
    set_info = CompanyIDSerializer(many=True, )

    class Meta:
        model = SiteReceptionGroup
        fields = ('id', 'title', 'group_id', 'avatar', 'manager', 'phone_number',
                  'email', 'desc', 'url', "set_info")

    def create(self, validated_data):
        company_list = validated_data.pop("set_info")

        for company in company_list:
            company_id = company["company_id"]
            sites = StationInfo.objects.filter(company_id=company_id)

            if not sites:
                # raise serializers.ValidationError(f"{company_id}该企业ID对应企业不存在")
                raise serializers.ValidationError({"error": f"{company_id}该企业ID对应企业不存在"})
            elif StationInfo.objects.get(company_id=company["company_id"]).set_up != None:
                # raise serializers.ValidationError(f"{company_id}该站点已添加接待组，请勿重复添加")
                raise serializers.ValidationError({"error": f"{company_id}该站点已添加接待组，请勿重复添加"})

        reception_group = SiteReceptionGroup.objects.create(**validated_data)

        for company in company_list:
            StationInfo.objects.all().filter(company_id=company["company_id"]).update(set_up=reception_group)
        return reception_group

    def update(self, instance, validated_data):
        company_list = validated_data.pop("set_info")
        for company in company_list:
            company_id = company["company_id"]
            sites = StationInfo.objects.filter(company_id=company_id).first()
            if not sites:
                raise serializers.ValidationError({"eror": f"{company_id}该企业ID对应企业不存在"})
            elif getattr(sites, 'set_up_id') and (getattr(sites, 'set_up_id') != instance.id):
                raise serializers.ValidationError({"error": f"{company_id}该站点对应其他客户经理，无法修改"})

        instance = super(SiteReceptionGroupSerializer, self).update(instance, validated_data)

        instance.set_info.clear()
        for company_id in company_list:
            StationInfo.objects.all().filter(company_id=company_id["company_id"]).update(set_up=instance)
        return instance
