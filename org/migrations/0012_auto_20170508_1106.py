# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-08 11:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0011_auto_20170428_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='decisionCycle',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterModelTable(
            name='organization',
            table='org',
        ),
    ]
