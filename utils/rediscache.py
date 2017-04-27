# -*- encoding: utf-8 -*-
"""
Topic: redis缓存管理器
"""
from django_redis import get_redis_connection
from django.core.cache import cache

RUNNING_TIMER = False
REDIS_DB = get_redis_connection('default')

