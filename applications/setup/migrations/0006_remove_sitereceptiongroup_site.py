# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-11 15:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0005_auto_20180426_1912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sitereceptiongroup',
            name='site',
        ),
    ]
