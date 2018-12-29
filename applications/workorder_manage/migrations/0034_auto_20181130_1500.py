# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-30 15:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('workorder_manage', '0033_auto_20181129_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='atta_matter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matter_ofatta', to='workorder_manage.Matter'),
        ),
        migrations.AlterField(
            model_name='matter',
            name='company_matter',
            field=models.CharField(max_length=16, null=True, verbose_name='企业id'),
        ),
        migrations.AlterField(
            model_name='matter',
            name='customer_feedback',
            field=models.TextField(null=True, verbose_name='客户反馈详情'),
        ),
        migrations.AlterField(
            model_name='reject',
            name='matter_reject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='of_matter', to='workorder_manage.Matter'),
        ),
        migrations.AlterField(
            model_name='remarkevolve',
            name='company',
            field=models.CharField(max_length=16, null=True, verbose_name='企业记录id'),
        ),
        migrations.AlterField(
            model_name='remarkevolve',
            name='matter',
            field=models.CharField(max_length=16, null=True, verbose_name='问题id'),
        ),
    ]
