# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-31 11:15
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import utils.customClass


class Migration(migrations.Migration):

    dependencies = [
        ('usersys', '0043_auto_20170728_1136'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='myuser',
            options={'permissions': (('as_investor', '\u6295\u8d44\u4eba\u8eab\u4efd\u7c7b\u578b'), ('as_trader', '\u4ea4\u6613\u5e08\u8eab\u4efd\u7c7b\u578b'), ('as_admin', '\u7ba1\u7406\u5458\u8eab\u4efd\u7c7b\u578b'), ('user_adduser', '\u7528\u6237\u65b0\u589e\u7528\u6237'), ('user_deleteuser', '\u7528\u6237\u5220\u9664\u7528\u6237(obj\u7ea7\u522b)'), ('user_changeuser', '\u7528\u6237\u4fee\u6539\u7528\u6237(obj\u7ea7\u522b)'), ('user_getuser', '\u7528\u6237\u67e5\u770b\u7528\u6237(obj\u7ea7\u522b)'), ('admin_adduser', '\u7ba1\u7406\u5458\u65b0\u589e\u7528\u6237'), ('admin_deleteuser', '\u7ba1\u7406\u5458\u5220\u9664'), ('admin_changeuser', '\u7ba1\u7406\u5458\u4fee\u6539\u7528\u6237\u57fa\u672c\u4fe1\u606f'), ('admin_getuser', '\u7ba1\u7406\u5458\u67e5\u770b\u7528\u6237'), ('user_addfavorite', '\u7528\u6237\u4e3b\u52a8\u63a8\u8350favorite(obj\u7ea7\u522b\u2014\u2014\u7ed9\u4ea4\u6613\u5e08\u7684)'), ('user_getfavorite', '\u7528\u6237\u67e5\u770bfavorite(obj\u7ea7\u522b\u2014\u2014\u7ed9\u4ea4\u6613\u5e08\u7684)'), ('user_interestproj', '\u7528\u6237\u4e3b\u52a8\u8054\u7cfbfavorite(obj\u7ea7\u522b\u2014\u2014\u7ed9\u6295\u8d44\u4eba\u7684)'))},
        ),
        migrations.AlterField(
            model_name='myuser',
            name='org',
            field=utils.customClass.MyForeignKey(blank=True, help_text='\u6240\u5c5e\u673a\u6784', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='org_users', to='org.organization'),
        ),
    ]
