#coding=utf-8
import traceback

from django.db import transaction
from rest_framework import filters
from rest_framework import viewsets

from sourcetype.models import Tag, TitleType, DataSource,Country,Industry, TransactionType, \
    TransactionPhases, OrgArea, CurrencyType, OrgType, CharacterType, ProjectStatus, TransactionStatus, orgtitletable, \
    webmenu, Service, OrgAttribute, BDStatus
from sourcetype.serializer import tagSerializer, countrySerializer, industrySerializer, \
    titleTypeSerializer, DataSourceSerializer, orgAreaSerializer, transactionTypeSerializer, transactionPhasesSerializer, \
    currencyTypeSerializer, orgTypeSerializer, characterTypeSerializer, ProjectStatusSerializer, \
    transactionStatuSerializer, OrgtitletableSerializer, WebMenuSerializer, serviceSerializer, orgAttributeSerializer, \
    BDStatusSerializer
from utils.customClass import  JSONResponse, InvestError
from utils.util import SuccessResponse, InvestErrorResponse, ExceptionResponse, returnListChangeToLanguage


class TagView(viewsets.ModelViewSet):
    """
        list:获取所有标签
        create:新增标签
        update:修改标签
        destroy:删除标签
    """

    queryset = Tag.objects.all().filter(is_deleted=False)
    serializer_class = tagSerializer

    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            source = request.META.get('HTTP_SOURCE', 1)
            queryset = self.filter_queryset(self.get_queryset()).filter(datasource=source)
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    # @loginTokenIsAvailable()
    # def create(self, request, *args, **kwargs):
    #     try:
    #         if not request.user.is_superuser:
    #             raise InvestError(2009,msg='没有操作权限')
    #         with transaction.atomic():
    #             lang = request.GET.get('lang')
    #             data = request.data
    #             serializer = self.serializer_class(data=data)
    #             if serializer.is_valid():
    #                  serializer.save()
    #             else:
    #                 raise InvestError(code=20071,msg='data有误_%s' % serializer.error_messages)
    #             return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
    #     except InvestError as err:
    #         return JSONResponse(InvestErrorResponse(err))
    #     except Exception:
    #         catchexcption(request)
    #         return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))
class ProjectStatusView(viewsets.ModelViewSet):
    """
        list:获取所有标签
        create:新增标签
        update:修改标签
        destroy:删除标签
    """
    queryset = ProjectStatus.objects.all().filter(is_deleted=False)
    serializer_class = ProjectStatusSerializer

    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class ServiceView(viewsets.ModelViewSet):
    """
        list:获取所有service
        create:新增service
        update:修改service
        destroy:删除service
    """
    queryset = Service.objects.all().filter(is_deleted=False)
    serializer_class = serviceSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    # def destroy(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         instance.is_deleted = True
    #         instance.save(update_fields=['is_deleted'])
    #         return JSONResponse(SuccessResponse({'is_deleted':instance.is_deleted}))
    #     except InvestError as err:
    #         return JSONResponse(InvestErrorResponse(err))
    #     except Exception:
    #         return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class CountryView(viewsets.ModelViewSet):
    """
        list:获取所有国家
        create:新增国家
        update:修改国家
        destroy:删除国家
    """
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    filter_fields = ('level', 'parent',)
    queryset = Country.objects.all().filter(is_deleted=False)
    serializer_class = countrySerializer

    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            source = request.META.get('HTTP_SOURCE',1)
            queryset = self.filter_queryset(self.get_queryset()).filter(datasource=source)
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    # def destroy(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         instance.is_deleted = True
    #         instance.save(update_fields=['is_deleted'])
    #         return JSONResponse(SuccessResponse({'is_deleted':instance.is_deleted}))
    #     except InvestError as err:
    #         return JSONResponse(InvestErrorResponse(err))
    #     except Exception:
    #         return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class CharacterTypeView(viewsets.ModelViewSet):
    """
        list:获取所有角色类型
        create:新增角色类型
        update:修改角色类型
        destroy:删除角色类型
    """
    # permission_classes = (IsSuperUser,)
    queryset = CharacterType.objects.all().filter(is_deleted=False)
    serializer_class = characterTypeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class IndustryView(viewsets.ModelViewSet):
    """
        list:获取所有行业
        create:新增行业
        update:修改行业
        destroy:删除行业
    """
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('isPindustry','Pindustry')
    queryset = Industry.objects.all().filter(is_deleted=False)
    serializer_class = industrySerializer

    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            source = request.META.get('HTTP_SOURCE', 1)
            queryset = self.filter_queryset(self.get_queryset()).filter(datasource=source)
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class TitleView(viewsets.ModelViewSet):
    """
        list:获取所有职位
        create:新增职位
        update:修改职位
        destroy:删除职位
    """
    queryset = TitleType.objects.all().filter(is_deleted=False)
    serializer_class = titleTypeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class BDStatusView(viewsets.ModelViewSet):
    """
        list:获取所有BD状态
        create:新增BD状态
        update:修改BD状态
        destroy:删除BD状态
    """
    queryset = BDStatus.objects.all().filter(is_deleted=False)
    serializer_class = BDStatusSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class DatasourceView(viewsets.ModelViewSet):
    """
        list:获取所有datasource
        create:新增datasource
        update:修改datasource
        destroy:删除datasource
    """
    queryset = DataSource.objects.all().filter(is_deleted=False)
    serializer_class = DataSourceSerializer


    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



class OrgAreaView(viewsets.ModelViewSet):
    """
        list:获取所有机构地区
        create:新增机构地区
        update:修改机构地区
        destroy:删除机构地区
    """
    queryset = OrgArea.objects.all().filter(is_deleted=False)
    serializer_class = orgAreaSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))
class TransactionTypeView(viewsets.ModelViewSet):
    """
        list:获取所有交易类型
        create:新增交易类型
        update:修改交易类型
        destroy:删除交易类型
    """
    queryset = TransactionType.objects.all().filter(is_deleted=False)
    serializer_class = transactionTypeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class TransactionPhasesView(viewsets.ModelViewSet):
    """
        list:获取所有机构轮次
        create:新增机构轮次
        update:修改机构轮次
        destroy:删除机构轮次
    """
    queryset = TransactionPhases.objects.all().filter(is_deleted=False)
    serializer_class = transactionPhasesSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class TransactionStatusView(viewsets.ModelViewSet):
    """
        list:获取所有时间轴状态
        create:新增时间轴状态
        update:修改时间轴状态
        destroy:删除时间轴状态
    """
    queryset = TransactionStatus.objects.all().filter(is_deleted=False)
    serializer_class = transactionStatuSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class OrgTypeView(viewsets.ModelViewSet):
    """
        list:获取所有机构类型
        create:新增机构类型
        update:修改机构类型
        destroy:删除机构类型
    """
    queryset = OrgType.objects.all().filter(is_deleted=False)
    serializer_class = orgTypeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = orgTypeSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class CurrencyTypeView(viewsets.ModelViewSet):
    """
        list:获取所有货币类型
        create:新增货币类型
        update:修改货币类型
        destroy:删除货币类型
    """
    queryset = CurrencyType.objects.all().filter(is_deleted=False)
    serializer_class = currencyTypeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class OrgAttributeView(viewsets.ModelViewSet):
    """
        list:获取所有机构属性
        create:新增机构属性
    """
    queryset = OrgAttribute.objects.all().filter(is_deleted=False)
    serializer_class = orgAttributeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class OrgtitletableView(viewsets.ModelViewSet):
    """
        list:获取所有机构类型职位对照
        create:新增机构类型职位对照
        update:修改机构类型职位对照
        destroy:删除机构类型职位对照
    """
    queryset = orgtitletable.objects.all().filter(is_deleted=False)
    serializer_class = OrgtitletableSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

def getmenulist(user):
    qslist = []
    allmenuobj = webmenu.objects.all()
    if user.has_perm('usersys.as_admin'):
        qslist.append(allmenuobj.filter(id__in=[5]))
    if user.has_perm('usersys.as_investor'):
        qslist.append(allmenuobj.filter(id__in=[13]))
    if user.has_perm('usersys.as_trader'):
        qslist.append(allmenuobj.filter(id__in=[12, 2]))
    if user.has_perm('org.admin_getorg'):#机构 、邮件管理
        qslist.append(allmenuobj.filter(id__in=[2, 3, 23]))
    if user.has_perm('proj.getBD')or user.has_perm('proj.manageBD'): # 项目bd管理
        qslist.append(allmenuobj.filter(id__in=[22, 23]))
    if user.has_perm('usersys.as_admin'):#日志查询
        qslist.append(allmenuobj.filter(id__in=[9]))
    if user.has_perm('msg.admin_manageSchedule'):#日程管理
        qslist.append(allmenuobj.filter(id__in=[25]))
    if user.has_perm('usersys.as_admin'):#日程查询
        qslist.append(allmenuobj.filter(id__in=[24, 26]))
    if user.is_superuser:
        qslist.append(allmenuobj.filter(id__in=[17]))
    if user.has_perm('proj.admin_addproj') or user.has_perm('proj.user_addproj'):
        qslist.append(allmenuobj.filter(id__in=[19]))
    qslist.append(allmenuobj.filter(id__in=[1, 4, 6, 7, 8, 10, 11, 14, 15, 16, 18, 20, 21, 27]))
    qsres = reduce(lambda x,y:x|y,qslist).distinct().order_by('index')
    return WebMenuSerializer(qsres,many=True).data