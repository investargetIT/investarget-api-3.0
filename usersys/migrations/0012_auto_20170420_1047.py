# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-20 10:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usersys', '0011_auto_20170420_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertags',
            name='deleteduser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='userdelete_usertags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usertags',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_usertags', to='sourcetype.Tag'),
        ),
    ]