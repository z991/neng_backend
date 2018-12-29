# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-20 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('version_manage', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='versionproduct',
            options={'permissions': (('view_versionproduct', 'Can see available versionproduct'),), 'verbose_name': '版本产品', 'verbose_name_plural': '版本产品'},
        ),
        migrations.AlterModelOptions(
            name='versionrepository',
            options={'permissions': (('view_versionrepository', 'Can see available versionrepository'),), 'verbose_name': '版本库表', 'verbose_name_plural': '版本库表'},
        ),
        migrations.AddField(
            model_name='versionrepository',
            name='parent',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='version_manage.VersionRepository', verbose_name='父版本'),
        ),
    ]
