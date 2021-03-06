# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-29 14:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('version_manage', '0008_auto_20181107_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='versionproduct',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='创建时间'),
        ),
        migrations.AlterField(
            model_name='versionproduct',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, help_text='更新时间'),
        ),
        migrations.AlterField(
            model_name='versionrepository',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='创建时间'),
        ),
        migrations.AlterField(
            model_name='versionrepository',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, help_text='更新时间'),
        ),
    ]
