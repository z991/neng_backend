# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-15 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorder_manage', '0019_auto_20181012_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyinfo',
            name='cli_version',
            field=models.IntegerField(blank=True, choices=[(1, 'B2B'), (2, 'B2C'), (3, '不限'), (4, 'B2B2C')], null=True),
        ),
        migrations.AlterField(
            model_name='stationinfo',
            name='cli_version',
            field=models.IntegerField(blank=True, choices=[(1, 'B2B'), (2, 'B2C'), (3, '不限'), (4, 'B2B2C')], null=True),
        ),
    ]
