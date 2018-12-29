# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-25 17:38
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('version_manage', '0003_versionproduct_product_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='versionproduct',
            name='release_date',
            field=models.DateField(default=datetime.date(2018, 9, 25)),
        ),
        migrations.AlterField(
            model_name='versionproduct',
            name='release_number',
            field=models.CharField(default='', max_length=5),
        ),
    ]
