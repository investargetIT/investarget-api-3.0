#coding=utf-8
import traceback

from django.core.paginator import Paginator, EmptyPage
from django.db import models
from django.db import transaction
from django.db.models import F
from django.db.models import Q,QuerySet, FieldDoesNotExist
from django.db.models.fields.reverse_related import ForeignObjectRel
from guardian.shortcuts import assign_perm
from rest_framework import filters, viewsets

from dataroom.models import dataroom, dataroomdirectoryorfile, publicdirectorytemplate
from dataroom.serializer import DataroomSerializer, DataroomCreateSerializer, DataroomdirectoryorfileCreateSerializer, \
    DataroomdirectoryorfileSerializer, DataroomdirectoryorfileUpdateSerializer
from proj.models import project
from usersys.models import MyUser
from utils.myClass import InvestError, JSONResponse
from utils.util import read_from_cache, write_to_cache, returnListChangeToLanguage, loginTokenIsAvailable, \
    returnDictChangeToLanguage, catchexcption, cache_delete_key, SuccessResponse, InvestErrorResponse, ExceptionResponse
import datetime


class DataroomView(viewsets.ModelViewSet):
    """
       list:dataroom列表
       create:新建dataroom
       update:关闭dataroom
       destroy:删除dataroom
    """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = dataroom.objects.all().filter(is_deleted=False)
    filter_fields = ('proj', 'investor', 'trader','isClose','user','isPublic')
    serializer_class = DataroomSerializer


    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            lang = request.GET.get('lang')
            userid = request.GET.get('user',None)
            projid = request.GET.get('proj',None)
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            if request.user.has_perm('dataroom.admin_getdataroom'):
                queryset = queryset
            else:
                if userid and isinstance(userid,(int,str)) and projid and isinstance(projid,(int,str)):
                    queryset = queryset.filter(user_id=userid,proj_id=projid)
                else:
                    queryset = queryset.filter(user=request.user)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = DataroomSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.admin_adddataroom', 'dataroom.user_adddataroom'])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            projid = data.get('proj',None)
            investorid = data.get('investor', None)
            traderid = data.get('trader', None)
            ispublic = data.get('isPublic',False)
            if not projid or not isinstance(projid,int):
                raise InvestError(20072,msg='proj 不能为空 int类型')
            try:
                proj = project.objects.get(id=projid,datasource=request.user.datasource,is_deleted=False)
            except project.DoesNotExist:
                raise InvestError(code=4002)
            if not ispublic:
                if not traderid or not investorid or not isinstance(investorid,int) or not isinstance(traderid,int):
                    raise InvestError(code=20072,msg='investor/trader bust be an nunull \'int\'')
            with transaction.atomic():
                responselist = []
                dataroomdata = {'proj':projid,'datasource':request.user.datasource.id,'supportor':proj.supportUser_id}
                projdataroom = self.get_queryset().filter(proj=proj,user_id=proj.supportUser_id)
                publicdataroom = self.get_queryset().filter(proj=proj, isPublic=True)
                if projdataroom.exists():
                    responselist.append(DataroomCreateSerializer(projdataroom.first()).data)
                else:
                    dataroomdata['user'] = proj.supportUser_id
                    dataroomdata['isPublic'] = False
                    supportordataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                    if supportordataroomserializer.is_valid():
                        supportordataroomserializer.save()
                        responselist.append(supportordataroomserializer.data)
                    else:
                        raise InvestError(code=20071, msg=supportordataroomserializer.errors)
                if publicdataroom.exists():
                    responselist.append(DataroomCreateSerializer(publicdataroom.first()).data)
                else:
                    dataroomdata['user'] = None
                    dataroomdata['isPublic'] = True
                    publicdataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                    if publicdataroomserializer.is_valid():
                        publicdataroom = publicdataroomserializer.save()
                        self.creatpublicdataroomdirectorywithtemplate(publicdataroomid=publicdataroom.id)
                        responselist.append(publicdataroomserializer.data)
                    else:
                        raise InvestError(code=20071, msg=publicdataroomserializer.errors)
                if not ispublic:
                    investordataroom = self.get_queryset().filter(proj=proj, user_id=investorid, trader_id=traderid,investor_id=investorid)
                    if investordataroom.exists():
                        responselist.append(DataroomCreateSerializer(investordataroom.first()).data)
                    else:
                        dataroomdata['user'] = investorid
                        dataroomdata['isPublic'] = False
                        dataroomdata['investor'] = investorid
                        dataroomdata['trader'] = traderid
                        dataroomdata['createuser'] = request.user.id
                        investordataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                        if investordataroomserializer.is_valid():
                            investordataroomserializer.save()
                            responselist.append(investordataroomserializer.data)
                        else:
                            raise InvestError(code=20071,msg=investordataroomserializer.errors)
                    traderdataroom = self.get_queryset().filter(proj=proj, user_id=traderid, trader_id=traderid,investor_id=investorid)
                    if traderdataroom.exists():
                        responselist.append(DataroomCreateSerializer(traderdataroom.first()).data)
                    else:
                        dataroomdata['user'] = traderid
                        dataroomdata['isPublic'] = False
                        dataroomdata['investor'] = investorid
                        dataroomdata['trader'] = traderid
                        dataroomdata['createuser'] = request.user.id
                        traderdataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                        if traderdataroomserializer.is_valid():
                            traderdataroomserializer.save()
                            responselist.append(traderdataroomserializer.data)
                        else:
                            raise InvestError(code=20071,msg=traderdataroomserializer.errors)
                return JSONResponse(
                    SuccessResponse(returnDictChangeToLanguage(responselist, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            traderid = data.get('trader', None)
            investorid = data.get('investor', None)
            projid = data.get('proj', None)
            if not data or not traderid or not investorid:
                raise InvestError(code=20071)
            dataroomquery = self.get_queryset().filter(isPublic=False, proj_id=projid, investor_id=investorid,trader_id=traderid)
            if not dataroomquery.exists():
                raise InvestError(code=6002)
            if request.user.has_perm('dataroom.admin_closedataroom'):
                pass
            elif request.user.has_perm('dataroom.user_closedataroom',dataroomquery.get(user_id=investorid)):
                pass
            else:
                raise InvestError(code=2009)
            self.get_queryset().filter(isPublic=False,proj_id=projid,investor_id=investorid,trader_id=traderid).update(isClose=True,closeDate=datetime.datetime.now())
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            data = request.data
            traderid = data.get('trader', None)
            investorid = data.get('investor', None)
            projid = data.get('proj', None)
            if not data or not traderid or not investorid:
                raise InvestError(code=20071)
            dataroomquery = self.get_queryset().filter(isPublic=False, proj_id=projid, investor_id=investorid, trader_id=traderid)
            if not dataroomquery.exists():
                raise InvestError(code=6002)
            if request.user.has_perm('dataroom.admin_deletedataroom'):
                pass
            elif request.user.has_perm('dataroom.user_deletedataroom',dataroomquery.get(user_id=investorid)):
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                for instance in dataroomquery:
                    rel_fileds = [f for f in dataroom._meta.get_fields() if isinstance(f, ForeignObjectRel)]
                    links = [f.get_accessor_name() for f in rel_fileds]
                    for link in links:
                        if link in []:
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
                                except FieldDoesNotExist:
                                    if manager.all().count():
                                        raise InvestError(code=2010, msg=u'{} 上有关联数据，且没有is_deleted字段'.format(link))
                        else:
                            manager = getattr(instance, link, None)
                            if not manager:
                                continue
                            # one to one
                            if isinstance(manager, models.Model):
                                if hasattr(manager, 'is_deleted') and not manager.is_deleted:
                                    manager.is_deleted = True
                                    manager.save()
                            else:
                                try:
                                    manager.model._meta.get_field('is_deleted')
                                    if manager.all().filter(is_deleted=False).count():
                                        manager.all().update(is_deleted=True)
                                except FieldDoesNotExist:
                                    if manager.all().count():
                                        raise InvestError(code=2010, msg=u'{} 上有关联数据,且没有is_deleted字段'.format(link))
                    instance.is_deleted = True
                    instance.deleteduser = request.user
                    instance.deletedtime = datetime.datetime.now()
                    instance.save()
                    instance.timeline_transationStatus.all().update(is_deleted=True)
                    instance.timeline_remarks.all().update(is_deleted=True)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(DataroomSerializer(dataroomquery,many=True))))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    #创建public模板
    def creatpublicdataroomdirectorywithtemplate(self,publicdataroomid):
        templatequery = publicdirectorytemplate.objects.all()
        topdirectories = templatequery.filter(parent=None)
        if topdirectories.exists():
            for directory in topdirectories:
                self.create_diractory(directoryname=directory.name,dataroom=publicdataroomid,templatedirectoryID=directory.id,orderNO=directory.orderNO,parent=None)
    #创建public模板
    def create_diractory(self,directoryname,dataroom,templatedirectoryID,orderNO,parent=None):
        directoryobj = dataroomdirectoryorfile(name=directoryname, dataroom_id=dataroom,orderNO=orderNO,parent_id=parent,createdtime=datetime.datetime.now(),createuser=self.request.user.id).save()
        sondirectoryquery = publicdirectorytemplate.objects.filter(parent=templatedirectoryID)
        if sondirectoryquery.exists():
            for sondirectory in sondirectoryquery:
                self.create_diractory(directoryname=sondirectory.name,dataroom=dataroom,templatedirectoryID=sondirectory.id,orderNO=sondirectory.orderNO,parent=directoryobj.id)


class DataroomdirectoryorfileView(viewsets.ModelViewSet):
    """
           list:dataroom文件或目录列表
           create:新建(复制)dataroom文件或目录
           update:移动目录或文件到目标位置
           destroy:删除dataroom文件或目录
        """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = dataroomdirectoryorfile.objects.all().filter(is_deleted=False)
    filter_fields = ('dataroom', 'parent','isFile')
    serializer_class = DataroomdirectoryorfileCreateSerializer
    Model = dataroomdirectoryorfile


    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(datasource=self.request.user.datasource)
            else:
                queryset = queryset.all()
        else:
            raise InvestError(code=8890)
        return queryset

    def get_object(self,pk=None):
        if pk:
            try:
                obj = self.Model.objects.get(id=pk, is_deleted=False)
            except self.Model.DoesNotExist:
                raise InvestError(code=7002, msg='dataroom with this "%s" is not exist' % pk)
        else:
            try:
                obj = self.Model.objects.get(id=self.kwargs['pk'], is_deleted=False)
            except self.Model.DoesNotExist:
                raise InvestError(code=7002,msg='dataroom with this （"%s"） is not exist' % self.kwargs['pk'])
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888,msg='资源非同源')
        return obj

    def get_dataroom(self,id):
        if self.request.user.is_anonymous:
            raise InvestError(code=8889)
        try:
            dataroomobj = dataroom.objects.get(id=id,is_deleted=False,datasource=self.request.user.datasource)
        except dataroom.DoesNotExist:
            raise InvestError(code=7002)
        return dataroomobj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            lang = request.GET.get('lang')
            dataroomid = request.GET.get('dataroom',None)
            parentid = request.GET.get('parent',None)
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            if dataroomid and isinstance(dataroomid,(int,str)):
                dataroomobj = self.get_dataroom(dataroomid)
                if request.user.has_perm('dataroom.admin_getdataroom'):
                    queryset = queryset.filter(parent_id=parentid)
                elif request.user.has_perm('dataroom.user_getdataroom', dataroomobj):
                    queryset = queryset.filter(dataroom=dataroomobj,parent_id=parentid)
                else:
                    raise InvestError(code=2009)
            else:
                raise InvestError(code=20072,msg='dataroom 不能空')
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
            except EmptyPage:
                raise InvestError(code=1001)
            queryset = queryset.page(page_index)
            serializer = DataroomdirectoryorfileSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            dataroomid = data.get('dataroom', None)
            if dataroomid:
                dataroomobj = self.get_dataroom(dataroomid)
                if request.user.has_perm('dataroom.admin_adddataroom'):
                    pass
                elif request.user.has_perm('dataroom.user_adddataroom', dataroomobj):
                    pass
                else:
                    raise InvestError(code=2009)
            else:
                raise InvestError(code=20072)
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            with transaction.atomic():
                directoryorfileserializer = DataroomdirectoryorfileCreateSerializer(data=data)
                if directoryorfileserializer.is_valid():
                    directoryorfile = directoryorfileserializer.save()
                else:
                    raise InvestError(code=20071, msg='data有误_%s'%directoryorfileserializer.errors)
                destquery = directoryorfile.parent.asparent_directories.exclude(pk=directoryorfile.pk).filter(is_deleted=False,orderNO__gte=directoryorfile.orderNO)
                if destquery.exist():
                    destquery.update(orderNO = F('orderNO')+ 1)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(directoryorfileserializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            fileid = data.get('fileid', None)
            if fileid:
                file = self.get_object(fileid)
                if request.user.has_perm('dataroom.admin_changedataroom'):
                    pass
                elif request.user.has_perm('dataroom.user_changedataroom', file.dataroom):
                    pass
                else:
                    raise InvestError(code=2009)
            else:
                raise InvestError(code=20072)
            data['lastmodifyuser'] = request.user.id
            data['lastmodifytime'] = datetime.datetime.now()
            with transaction.atomic():
                directoryorfileserializer = DataroomdirectoryorfileUpdateSerializer(file,data=data)
                if directoryorfileserializer.is_valid():
                    directoryorfile = directoryorfileserializer.save()
                else:
                    raise InvestError(code=20071, msg='data有误_%s'%directoryorfileserializer.errors)
                destquery = directoryorfile.parent.asparent_directories.exclude(pk=directoryorfile.pk).filter(is_deleted=False,orderNO__gte=directoryorfile.orderNO)
                if destquery.exist():
                    destquery.update(orderNO = F('orderNO')+ 1)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(directoryorfileserializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



    @loginTokenIsAvailable()
    def destroy(self, request, *args, **kwargs):
        try:
            filelist = request.data.get('filelist',None)
            if not isinstance(filelist,list) or not filelist:
                raise InvestError(code=20071,msg='need an id list')
            with transaction.atomic():
                for fileid in filelist:
                    instance = self.get_object(fileid)
                    if request.user.has_perm('dataroom.admin_deletedataroom'):
                        pass
                    elif request.user.has_perm('dataroom.user_deletedataroom', instance):
                        pass
                    else:
                        raise InvestError(code=2009, msg='没有权限')
                    if instance.checkDirectoryHasFile():
                        raise InvestError(code=7006)
                    else:
                        self.deleteEmptyDirectory(instance,request.user)
                return JSONResponse(SuccessResponse(filelist))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    def deleteEmptyDirectory(self,instance,deleteuser=None):
        if not isinstance(instance,dataroomdirectoryorfile):
            raise InvestError(7007,msg='expect a dataroomdirectoryorfile type but get a %s type'%type(instance))
        if deleteuser and not isinstance(deleteuser,MyUser):
            raise InvestError(7007,msg='expect an authenticated user type but get a %s type'%type(instance))
        if instance.is_deleted:
            raise InvestError(code=7002)
        if instance.checkIsEmptyDirectory:
            raise InvestError(7006)
        else:
            filequery = instance.asparent_directories.filter(is_deleted=False)
            if filequery.count():
                for fileordirectoriey in filequery:
                   fileordirectoriey.deleteEmptyDirectory()
            else:
                instance.is_deleted = True
                instance.deleteduser = deleteuser
                instance.deletedtime = datetime.datetime.now()
                instance.save()