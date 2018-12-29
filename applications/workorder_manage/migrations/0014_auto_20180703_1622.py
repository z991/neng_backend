# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-03 16:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorder_manage', '0013_auto_20180604_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stationinfo',
            name='amount_cashed',
            field=models.CharField(blank=True, default='', max_length=12, null=True, verbose_name='回款金额'),
        ),
        migrations.AlterField(
            model_name='stationinfo',
            name='contract_amount',
            field=models.CharField(blank=True, default='', max_length=12, null=True, verbose_name='合同金额'),
        ),
    ]
