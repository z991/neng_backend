import logging

from django.db import transaction
from rest_framework import serializers
from .models import VersionRepository, VersionProduct

log = logging.getLogger('django')


class VersionRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionRepository
        fields = ('id', 'version_id', 'release_status', 'release_number', 'parent')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                version_info = super(VersionRepositorySerializer, self).create(validated_data)
                # 父版本id
                parent = self.initial_data.get('parent', '')
                if parent:
                    version_info.parent = VersionRepository.objects.get(pk=parent)

                version_info.save()
                return version_info

        except Exception as e:
            log.error(e)
            raise TypeError(e)

    def update(self, instance, validated_data):
        instance = super(VersionRepositorySerializer, self).update(instance, validated_data)
        # 父版本id
        parent = self.initial_data.get('parent', '')
        if parent:
            instance.parent = VersionRepository.objects.get(pk=parent)
        instance.save()
        return instance


class VersionProductSerializer(serializers.ModelSerializer):
    version_id = VersionRepositorySerializer(read_only=True)

    class Meta:
        model = VersionProduct
        fields = ('id', 'version_id', 'release_status', 'release_number', 'product_version',
                  'release_date', 'product_name', 'product_explain', 'product_classify','schedule')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                print('validated_data==', type(validated_data), validated_data)
                version_info = super(VersionProductSerializer, self).create(validated_data)
                # 版本id
                version_id = self.initial_data.get('version_id', '')

                version_info.version_id = VersionRepository.objects.get(pk=version_id)
                release_number = self.initial_data.get('release_number', '')
                # if release_number:
                version_info.release_number = '0'

                version_info.save()
                return version_info

        except Exception as e:
            log.error(e)
            raise TypeError(e)
