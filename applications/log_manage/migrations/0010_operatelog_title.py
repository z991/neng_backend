# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-30 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log_manage', '0009_auto_20181029_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='operatelog',
            name='title',
            field=models.CharField(max_length=128, null=True, verbose_name='修改的标题'),
        ),
    ]
