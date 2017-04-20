#coding=utf-8
import traceback
from django.core.paginator import Paginator, EmptyPage
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.reverse_related import ForeignObjectRel
from rest_framework import filters
from rest_framework import viewsets
import datetime
from org.models import orgTransactionPhase
from proj.models import project, finance, favorite, projectTags, projectIndustries, projectTransactionType
from proj.serializer import ProjSerializer, FavoriteSerializer,FinanceSerializer, ProjCreatSerializer, \
    ProjCommonSerializer
from sourcetype.models import Tag, Industry, TransactionType
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
            tagsdata = projdata.pop('tags',None)
            industrydata = projdata.pop('industries',None)
            transactiontypedata = projdata.pop('transactionType',None)
            with transaction.atomic():
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
                    if tagsdata:
                        tagslist = []
                        for transactionPhase in tagsdata:
                            tagslist.append(projectTags(proj=pro, tag_id=transactionPhase,createuser=request.user))
                        pro.project_tags.bulk_create(tagslist)
                    if industrydata:
                        industrylist = []
                        for transactionPhase in industrydata:
                            industrylist.append(projectTags(proj=pro, industry_id=transactionPhase,createuser=request.user))
                        pro.project_industries.bulk_create(industrylist)
                    if transactiontypedata:
                        transactiontypelist = []
                        for transactionPhase in tagsdata:
                            transactiontypelist.append(projectTags(proj=pro, transactionType_id=transactionPhase,createuser=request.user))
                        pro.project_TransactionTypes.bulk_create(transactiontypelist)
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
    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            pro = self.get_object()
            if request.user.has_perm('proj.admin_changeproj'):
                pass
            elif request.user.has_perm('proj.user_changeproj',pro):
                pass
            else:
                raise InvestError(code=2009,msg='非上传方或管理员无法修改项目')
            projdata = request.data
            projdata['lastmodifyuser'] = request.user.id
            projdata['lastmodifytime'] = datetime.datetime.now()
            tagsdata = projdata.pop('tags', None)
            industrydata = projdata.pop('industries', None)
            transactiontypedata = projdata.pop('transactionType', None)
            with transaction.atomic():
                proj = ProjCreatSerializer(data=projdata)
                if proj.is_valid():
                    pro = proj.save()
                    if tagsdata:
                        taglist = Tag.objects.in_bulk(tagsdata)
                        addlist = [item for item in taglist if item not in pro.tags.all()]
                        removelist = [item for item in pro.tags.all() if item not in taglist]
                        pro.project_tags.filter(tag__in=removelist, is_deleted=False).update(is_deleted=True,
                                                                                           deletedtime=datetime.datetime.now(),
                                                                                           deleteduser=request.user)
                        usertaglist = []
                        for tag in addlist:
                            usertaglist.append(projectTags(proj=pro, tag=tag, createuser=request.user))
                        pro.project_tags.bulk_create(usertaglist)

                    if industrydata:
                        industrylist = Industry.objects.in_bulk(industrydata)
                        addlist = [item for item in industrylist if item not in pro.industries.all()]
                        removelist = [item for item in pro.industries.all() if item not in industrylist]
                        pro.project_industries.filter(industry__in=removelist, is_deleted=False).update(is_deleted=True,
                                                                                           deletedtime=datetime.datetime.now(),
                                                                                           deleteduser=request.user)
                        projindustrylist = []
                        for industry in addlist:
                            projindustrylist.append(projectIndustries(proj=pro, industry=industry, createuser=request.user))
                        pro.project_industries.bulk_create(projindustrylist)

                    if transactiontypedata:
                        transactionTypelist = TransactionType.objects.in_bulk(tagsdata)
                        addlist = [item for item in transactionTypelist if item not in pro.transactionType.all()]
                        removelist = [item for item in pro.transactionType.all() if item not in transactionTypelist]
                        pro.project_tags.filter(transactionType__in=removelist, is_deleted=False).update(is_deleted=True,
                                                                                           deletedtime=datetime.datetime.now(),
                                                                                           deleteduser=request.user)
                        projtransactiontypelist = []
                        for transactionPhase in addlist:
                            projtransactiontypelist.append(projectTags(proj=pro, transactionType=transactionPhase, createuser=request.user))
                            pro.project_tags.bulk_create(projtransactiontypelist)

                else:
                    raise InvestError(code=4001,
                                      msg='data有误_%s\n%s' % (proj.error_messages, proj.errors))
                return JSONResponse(
                    {'success': True, 'result': ProjSerializer(pro).data, 'errorcode': 1000, 'errormsg': None})
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if request.user.has_perm('proj.admin_deleteproj'):
                pass
            elif request.user.has_perm('proj.user_deleteproj',instance):
                pass
            else:
                raise InvestError(code=2009)
            rel_fileds = [f for f in instance._meta.get_fields() if isinstance(f, ForeignObjectRel)]
            links = [f.get_accessor_name() for f in rel_fileds]
            for link in links:
                manager = getattr(instance, link, None)
                if not manager:
                    continue
                # one to one
                if isinstance(manager, models.Model):
                    if hasattr(manager, 'is_deleted') and not manager.is_deleted:
                        raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
                else:
                    try:
                        manager.model._meta.get_field('is_deleted')
                        if manager.all().filter(is_deleted=False).count():
                            raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
                    except FieldDoesNotExist as ex:
                        if manager.all().count():
                            raise InvestError(code=2010, msg=u'{} 上有关联数据'.format(link))
            with transaction.atomic():
                instance.is_deleted = True
                # instance.deleteduser = request.user
                instance.deletetime = datetime.datetime.utcnow()
                instance.save()
                response = {'success': True, 'result': ProjSerializer(instance).data, 'errorcode': 1000,
                            'errormsg': None}
                return JSONResponse(response)
        except InvestError as err:
            return JSONResponse({'success': False, 'result': None, 'errorcode': err.code, 'errormsg': err.msg})
        except Exception:
            catchexcption(request)
            return JSONResponse({'success': False, 'result': None, 'errorcode': 9999,
                                 'errormsg': traceback.format_exc().split('\n')[-2]})








