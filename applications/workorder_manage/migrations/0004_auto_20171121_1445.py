# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-21 06:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workorder_manage', '0003_companyinfo_abbreviation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountconf',
            name='set_pwd',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
