# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-24 10:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('msg', '0003_auto_20170510_1557'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='title',
            new_name='messagetitle',
        ),
    ]
