# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-17 07:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('production_manage', '0005_auto_20171017_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='ser_version',
        ),
    ]
