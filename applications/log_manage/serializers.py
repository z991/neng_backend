from rest_framework import serializers

from libs.datetimes import datetime_to_str, DATE_FORMAT, TIME_FORMAT
from .models import OperateLog


class OperateLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    created_time = serializers.SerializerMethodField()

    class Meta:
        model = OperateLog
        fields = ('id', 'operationmodule','username', 'created_date', 'created_time', 'action', 'title')

    def get_username(self, data):
        if data.user:
            return data.user.last_name

    def get_created_date(self, data):
        return datetime_to_str(data.operationtime, format=DATE_FORMAT)

    def get_created_time(self, data):
        return datetime_to_str(data.operationtime, format=TIME_FORMAT)


class PersonalLogSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()
    created_time = serializers.SerializerMethodField()

    class Meta:
        model = OperateLog
        fields = ('id', 'created_date', 'created_time', 'action', 'operationmodule', 'title')

    def get_created_date(self, data):
        return datetime_to_str(data.operationtime, format=DATE_FORMAT)

    def get_created_time(self, data):
        return datetime_to_str(data.operationtime, format=TIME_FORMAT)
