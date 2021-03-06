# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-13 20:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertising',
            name='ad_image',
            field=models.URLField(default='', verbose_name='广告轮播图'),
        ),
        migrations.AlterField(
            model_name='advertising',
            name='ad_position',
            field=models.IntegerField(choices=[(0, '首页轮播图'), (1, '列表轮播图')], default=0, verbose_name='广告位置'),
        ),
        migrations.AlterField(
            model_name='advertising',
            name='ad_put_operator',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='advertising', to=settings.AUTH_USER_MODEL, verbose_name='广告上架操作人'),
        ),
        migrations.AlterField(
            model_name='advertising',
            name='ad_status',
            field=models.IntegerField(choices=[(1, '上架'), (2, '下架'), (3, '待上架')], default=3, verbose_name='广告上架状态'),
        ),
    ]
