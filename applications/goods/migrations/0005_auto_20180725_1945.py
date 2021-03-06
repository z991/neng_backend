# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-25 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0004_auto_20180511_1533'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameteroptions',
            name='multiple_goods',
        ),
        migrations.AddField(
            model_name='parameteroptions',
            name='multiple_goods',
            field=models.ManyToManyField(blank=True, related_name='multiple_par_options', to='goods.MultipleGoods', verbose_name='行业解决方案'),
        ),
        migrations.RemoveField(
            model_name='parameteroptions',
            name='single_goods',
        ),
        migrations.AddField(
            model_name='parameteroptions',
            name='single_goods',
            field=models.ManyToManyField(blank=True, related_name='par_options', to='goods.SingleGoods', verbose_name='单价产品'),
        ),
    ]
