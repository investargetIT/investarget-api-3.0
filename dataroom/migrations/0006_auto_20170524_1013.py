# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-24 10:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataroom', '0005_auto_20170511_1128'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataroomdirectoryorfile',
            old_name='name',
            new_name='filename',
        ),
    ]
