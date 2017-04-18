#coding=utf-8
import traceback
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q, datetime
from rest_framework import filters
from rest_framework import viewsets
from proj.models import project, finance, favorite
from proj.serializer import ProjSerializer, FavoriteSerializer,FormatSerializer,FinanceSerializer, ProjCreatSerializer, \
    ProjCommonSerializer
from utils.util import catchexcption, read_from_cache, write_to_cache, loginTokenIsAvailable
from utils.myClass import JSONResponse, InvestError


class ProjectView(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    queryset = project.objects.filter(is_deleted=False)
    filter_fields = ('titleC', 'titleE',)
    serializer_class = ProjSerializer
    redis_key = 'project'
    Model = project

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        obj = read_from_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg])
        if not obj:
            try:
                obj = self.Model.objects.get(id=self.kwargs[lookup_url_kwarg], is_deleted=False)
            except self.Model.DoesNotExist:
                raise InvestError('obj with this "%s" is not exist' % self.kwargs[lookup_url_kwarg])
            else:
                write_to_cache(self.redis_key + '_%s' % self.kwargs[lookup_url_kwarg], obj)
        return obj

    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('page_size')
        page_index = request.GET.get('page_index')  # 从第一页开始
        if not page_size:
            page_size = 10
        if not page_index:
            page_index = 1
        queryset = self.filter_queryset(self.queryset)
        if request.user.is_anonymous:
            queryset = queryset.filter(isHidden=False)
        else:
            if request.user.has_perm('proj.admin_getproj'):
                queryset = queryset
            else:
                queryset = queryset.filter(Q(isHidden=False) | Q(createuser=request.user))
        try:
            queryset = Paginator(queryset, page_size)
        except EmptyPage:
            return JSONResponse({'success': True, 'result': [], 'errorcode': 1000, 'errormsg': None})
        queryset = queryset.page(page_index)
        serializer = ProjCommonSerializer(queryset, many=True)
        return JSONResponse({'success': True, 'result': serializer.data, 'errorcode': 1000, 'errormsg': None})


    @loginTokenIsAvailable(['proj.admin_addproj','proj.user_addproj'])
    def create(self, request, *args, **kwargs):
        try:
            projdata = request.data
            projdata['createuser'] = request.user.id
            financesdata = projdata.pop('finances',None)
            formatdata = projdata.pop('format',None)
            with transaction.atomic():
                if formatdata:
                    formatdata['createuser'] = request.user.id
                    format = FormatSerializer(data=formatdata)
                    if format.is_valid():
                        projFormat = format.save()
                        projdata['projFormat'] = projFormat.pk
                    else:
                        raise InvestError(code=4001, msg='format_%s'%format.error_messages)
                else:
                    raise InvestError(code=4001,msg='formatdata缺失')
                proj = ProjCreatSerializer(data=projdata)
                if proj.is_valid():
                    pro = proj.save()
                    if financesdata:
                        for f in financesdata:
                            f['proj'] = pro.pk
                            f['createuser'] = request.user.id
                        finances = FinanceSerializer(data=financesdata,many=True)
                        if finances.is_valid():
                           finances.save()
                        else:
                            raise InvestError(code=4001,
                                              msg='财务信息有误_%s\n%s' % (finances.error_messages, finances.errors))
                else:
                    raise InvestError(code=4001,
                                          msg='data有误_%s\n%s' % (proj.error_messages, proj.errors))
                return JSONResponse({'success':True,'result': ProjSerializer(pro).data,'errorcode':1000,'errormsg':None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            if request.user.has_perm('proj.admin_getproj'):
                serializerclass = ProjSerializer
            else:
                serializerclass = ProjSerializer
            instance = self.get_object()
            serializer = serializerclass(instance)
            return JSONResponse({'success': True, 'result': serializer.data, 'errorcode': 1000, 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    # def update(self, request, *args, **kwargs):
    #     data = request.data
    #     data['lastmodifyuser'] = request.user.id
    #     data['lastmodifytime'] = datetime.datetime.now()
    #     try:
    #         org = self.get_object()
    #         if request.user.has_perm('org.admin_changeorg'):
    #             pass
    #         elif request.user.has_perm('org.user_changeorg', org):
    #             pass
    #         else:
    #             raise InvestError(code=2009)
    #         with transaction.atomic():
    #             formatdata = data.pop('format', None)
    #             financesdata = data.pop('finanaces',None)
    #             projserializer = ProjCreatSerializer(org, data=data)
    #             if projserializer.is_valid():
    #                 org = projserializer.save()
    #                 if formatdata:
    #                     orgTransactionPhaselist = []
    #                     for transactionPhase in orgTransactionPhases:
    #                         orgTransactionPhaselist.append(
    #                             orgTransactionPhase(org=org, transactionPhase_id=transactionPhase, ))
    #                     org.org_orgTransactionPhases.bulk_create(orgTransactionPhaselist)
    #             else:
    #                 raise InvestError(code=20071,
    #                                   msg='data有误_%s\n%s' % (orgserializer.error_messages, orgserializer.errors))
    #             return JSONResponse(
    #                 {'success': True, 'result': OrgSerializer(org).data, 'errorcode': 1000, 'errormsg': None})
    #     except InvestError as err:
    #         return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
    #     except Exception:
    #         catchexcption(request)
    #         return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
    #                              'errormsg': traceback.format_exc().split('\n')[-2]})








