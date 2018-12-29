# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-25 19:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('setup', '0007_loginldapconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_source', models.SmallIntegerField(choices=[(1, '来自ldap'), (2, '来自本地')], default=1, verbose_name='创建来源')),
                ('is_enable', models.SmallIntegerField(choices=[(0, '软删'), (1, '正常')], default=1, verbose_name='是否软删除')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='loginldapconfig',
            name='login_model',
            field=models.SmallIntegerField(choices=[(1, 'LDAP登录模式'), (2, '本地登录模式'), (3, '本地+LDAP模式'), (4, 'LDAP+本地模式')], default=2),
        ),
    ]
