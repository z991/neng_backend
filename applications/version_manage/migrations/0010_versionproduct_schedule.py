# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-18 10:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('version_manage', '0009_auto_20181129_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='versionproduct',
            name='schedule',
            field=models.TextField(default='[{"name": "项目立项","time": "2018-12-18 10:06:47","mileage": "1","index": 1},{"name": "产品设计","time": "","mileage": "0","index": 2},{"name": "研发","time": "","mileage": "","index": 3},{"name": "测试","time": "","mileage": "","index": 4},{"name": "产品验收","time": "","mileage": "","index": 5},{"name": "部署","time": "","mileage": "","index": 6},{"name": "发版","time": "","mileage": "","index": 7},{"button_log": {"old": "无","new": "无"},"index": 8}]'),
        ),
    ]
