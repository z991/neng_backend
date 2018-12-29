# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-18 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorder_manage', '0025_auto_20181018_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinfo',
            name='station_type',
            field=models.IntegerField(choices=[(1, '试用客户'), (2, '正式客户'), (3, '市场渠道客户'), (4, '商务渠道客户'), (5, '自用站点')], null=True),
        ),
    ]
