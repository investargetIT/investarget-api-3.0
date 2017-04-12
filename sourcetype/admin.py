from django.contrib import admin

# Register your models here.
from .models import TransactionType, TransactionPhases,School, Specialty,OrgArea, Tag, Industry, CurrencyType, \
    AuditStatus, ProjectStatus, OrgType, FavoriteType, MessageType, ClientType, TitleType, Continent, Country

admin.site.register(ProjectStatus)
admin.site.register(AuditStatus)
admin.site.register(FavoriteType)
admin.site.register(Tag)
admin.site.register(CurrencyType)