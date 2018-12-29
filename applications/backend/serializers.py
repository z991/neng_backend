from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import LdapUser, LdapRole


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = LdapUser
        fields = ('username', 'email', 'password',)


class Groupserializer(serializers.ModelSerializer):
    class Meta:
        model = LdapRole
        field = ('ouname',)
