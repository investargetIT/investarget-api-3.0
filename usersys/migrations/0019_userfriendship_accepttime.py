# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-05 16:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersys', '0018_auto_20170505_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='userfriendship',
            name='accepttime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]