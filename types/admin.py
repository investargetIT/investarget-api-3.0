from django.contrib import admin

# Register your models here.
from .models import projectStatus,userStatus,orgStatus,favoriteType
#
admin.site.register(projectStatus)
admin.site.register(userStatus)
admin.site.register(orgStatus)
admin.site.register(favoriteType)