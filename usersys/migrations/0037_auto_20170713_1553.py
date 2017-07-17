# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-13 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersys', '0036_auto_20170619_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mytoken',
            name='created',
            field=models.DateTimeField(auto_now_add=True, help_text='CreatedTime', null=True),
        ),
        migrations.AlterField(
            model_name='userfriendship',
            name='createdtime',
            field=models.DateTimeField(auto_created=True, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userrelation',
            name='createdtime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='usertags',
            name='createdtime',
            field=models.DateTimeField(auto_created=True, blank=True, null=True),
        ),
    ]
