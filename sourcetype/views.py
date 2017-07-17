#coding=utf-8
import traceback

from rest_framework import filters
from rest_framework import viewsets

from sourcetype.models import Tag, TitleType, DataSource,Continent,Country,Industry, TransactionType, \
    TransactionPhases, OrgArea, CurrencyType, OrgType, CharacterType, ProjectStatus
from sourcetype.serializer import tagSerializer, countrySerializer, industrySerializer, continentSerializer, \
    titleTypeSerializer, DataSourceSerializer, orgAreaSerializer, transactionTypeSerializer, transactionPhasesSerializer, \
    currencyTypeSerializer, orgTypeSerializer, characterTypeSerializer, ProjectStatusSerializer
from utils.customClass import IsSuperUser, JSONResponse, InvestError
from utils.util import SuccessResponse, InvestErrorResponse, ExceptionResponse, returnListChangeToLanguage


class TagView(viewsets.ModelViewSet):
    """
        list:获取所有标签
        create:新增标签
        update:修改标签
        destroy:删除标签
    """
    # permission_classes = (IsSuperUser,)
    queryset = Tag.objects.all().filter(is_deleted=False)
    serializer_class = tagSerializer

    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = tagSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class ProjectStatusView(viewsets.ModelViewSet):
    """
        list:获取所有标签
        create:新增标签
        update:修改标签
        destroy:删除标签
    """
    # permission_classes = (IsSuperUser,)
    queryset = ProjectStatus.objects.all().filter(is_deleted=False)
    serializer_class = ProjectStatusSerializer

    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = ProjectStatusSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class CountryView(viewsets.ModelViewSet):
    """
        list:获取所有国家
        create:新增国家
        update:修改国家
        destroy:删除国家
    """
    # permission_classes = (IsSuperUser,)
    queryset = Country.objects.all().filter(is_deleted=False)
    serializer_class = countrySerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = countrySerializer(queryset, many=True)
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
            serializer = characterTypeSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

class ContinentalView(viewsets.ModelViewSet):
    """
        list:获取所有大洲
        create:新增大洲
        update:修改大洲
        destroy:删除大洲
    """
    # permission_classes = (IsSuperUser,)
    queryset = Continent.objects.all().filter(is_deleted=False)
    serializer_class = continentSerializer

    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = continentSerializer(queryset, many=True)
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
    # permission_classes = (IsSuperUser,)
    queryset = Industry.objects.all().filter(is_deleted=False)
    serializer_class = industrySerializer

    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = industrySerializer(queryset, many=True)
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
    # permission_classes = (IsSuperUser,)
    queryset = TitleType.objects.all().filter(is_deleted=False)
    serializer_class = titleTypeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = titleTypeSerializer(queryset, many=True)
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
    # permission_classes = (IsSuperUser,)
    queryset = DataSource.objects.all().filter(is_deleted=False)
    serializer_class = DataSourceSerializer


    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = DataSourceSerializer(queryset, many=True)
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
    # permission_classes = (IsSuperUser,)
    queryset = OrgArea.objects.all().filter(is_deleted=False)
    serializer_class = orgAreaSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = orgAreaSerializer(queryset, many=True)
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
    # permission_classes = (IsSuperUser,)
    queryset = TransactionType.objects.all().filter(is_deleted=False)
    serializer_class = transactionTypeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = transactionTypeSerializer(queryset, many=True)
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
    # permission_classes = (IsSuperUser,)
    queryset = TransactionPhases.objects.all().filter(is_deleted=False)
    serializer_class = transactionPhasesSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = transactionPhasesSerializer(queryset, many=True)
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
    # permission_classes = (IsSuperUser,)
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
    # permission_classes = (IsSuperUser,)
    queryset = CurrencyType.objects.all().filter(is_deleted=False)
    serializer_class = currencyTypeSerializer
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            queryset = self.filter_queryset(self.get_queryset())
            serializer = currencyTypeSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data,lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

