# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-07 14:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log_manage', '0010_operatelog_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detaillog',
            name='new_value',
            field=models.TextField(null=True, verbose_name='新值'),
        ),
        migrations.AlterField(
            model_name='detaillog',
            name='old_value',
            field=models.TextField(null=True, verbose_name='旧值'),
        ),
        migrations.AlterField(
            model_name='operatelog',
            name='action',
            field=models.PositiveSmallIntegerField(choices=[(1, '新增'), (2, '删除'), (3, '修改'), (4, '登录'), (5, '退出'), (500, '其他'), (6, '浏览'), (110, '脚本执行')], null=True),
        ),
    ]
