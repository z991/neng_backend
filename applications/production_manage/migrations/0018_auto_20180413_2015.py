# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-13 20:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production_manage', '0017_auto_20180110_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='functioninfo',
            name='cli_version',
            field=models.IntegerField(choices=[(1, 'B2B'), (2, 'B2C'), (3, '不限'), (4, 'B2B2C')]),
        ),
    ]
