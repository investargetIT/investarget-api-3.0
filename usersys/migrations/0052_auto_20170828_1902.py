# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-28 19:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usersys', '0051_auto_20170821_1037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userfriendship',
            options={'permissions': (('admin_addfriend', '\u7ba1\u7406\u5458\u5efa\u7acb\u7528\u6237\u597d\u53cb\u5173\u7cfb'), ('admin_changefriend', '\u7ba1\u7406\u5458\u4fee\u6539\u7528\u6237\u597d\u53cb\u5173\u7cfb'), ('admin_deletefriend', '\u7ba1\u7406\u5458\u5220\u9664\u7528\u6237\u597d\u53cb\u5173\u7cfb'), ('admin_getfriend', '\u7ba1\u7406\u5458\u67e5\u770b\u7528\u6237\u597d\u53cb\u5173\u7cfb'), ('user_addfriend', '\u7528\u6237\u5efa\u7acb\u7528\u6237\u597d\u53cb\u5173\u7cfb\uff08\u672a\u5ba1\u6838\u7528\u6237\u4e0d\u8981\u7ed9\uff09'))},
        ),
    ]