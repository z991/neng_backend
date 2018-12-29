from rest_framework import serializers
from .models import ClientDownload


class ClientDownloadSerializers(serializers.ModelSerializer):
    '''
    客户端下载
    '''
    class Meta:
        model = ClientDownload
        fields = ('id', 'version_num', 'down_address', 'classify')