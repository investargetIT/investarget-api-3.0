#coding=utf-8
import traceback

from django.core.paginator import Paginator, EmptyPage
from django.db import models
from django.db import transaction
from django.db.models import F
from django.db.models import Q,QuerySet, FieldDoesNotExist
from django.db.models.fields.reverse_related import ForeignObjectRel
from rest_framework import filters, viewsets

from dataroom.models import dataroom, dataroomdirectoryorfile, publicdirectorytemplate, dataroom_User_file
from dataroom.serializer import DataroomSerializer, DataroomCreateSerializer, DataroomdirectoryorfileCreateSerializer, \
    DataroomdirectoryorfileSerializer, DataroomdirectoryorfileUpdateSerializer, User_DataroomfileSerializer, \
    User_DataroomSerializer, User_DataroomfileCreateSerializer
from proj.models import project
from third.views.qiniufile import deleteqiniufile
from utils.customClass import InvestError, JSONResponse, RelationFilter
from utils.sendMessage import sendmessage_dataroomfileupdate
from utils.util import read_from_cache, write_to_cache, returnListChangeToLanguage, loginTokenIsAvailable, \
    returnDictChangeToLanguage, catchexcption, cache_delete_key, SuccessResponse, InvestErrorResponse, ExceptionResponse, \
    logexcption, add_perm
import datetime
from django_filters import FilterSet

class DataroomFilter(FilterSet):
    supportuser = RelationFilter(filterstr='proj__supportUser',lookup_method='in')
    proj = RelationFilter(filterstr='proj', lookup_method='in')
    isClose = RelationFilter(filterstr='isClose', lookup_method='in')
    class Meta:
        model = dataroom
        fields = ('proj', 'isClose', 'supportuser')

class DataroomView(viewsets.ModelViewSet):
    """
       list:dataroom列表
       create:新建dataroom
       retrieve:查看dataroom目录结构
       update:关闭dataroom
       destroy:删除dataroom
    """
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend,)
    queryset = dataroom.objects.all().filter(is_deleted=False)
    search_fields = ('proj__projtitleC', 'proj__supportUser__usernameC')
    filter_class = DataroomFilter
    serializer_class = DataroomSerializer

    def get_object(self):
        lookup_url_kwarg = 'pk'
        try:
            obj = dataroom.objects.get(id=self.kwargs[lookup_url_kwarg], is_deleted=False)
        except dataroom.DoesNotExist:
            raise InvestError(code=6002,msg='timeline with this "%s" is not exist' % self.kwargs[lookup_url_kwarg])
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888,msg='资源非同源')
        return obj


    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            page_size = request.GET.get('page_size')
            page_index = request.GET.get('page_index')  # 从第一页开始
            lang = request.GET.get('lang')
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset()).filter(datasource=self.request.user.datasource)
            sort = request.GET.get('sort')
            if sort not in ['True', 'true', True, 1, 'Yes', 'yes', 'YES', 'TRUE']:
                queryset = queryset.order_by('-lastmodifytime', '-createdtime')
            else:
                queryset = queryset.order_by('lastmodifytime', 'createdtime')
            if request.user.has_perm('dataroom.admin_getdataroom'):
                queryset = queryset
            else:
                queryset = queryset.filter(id__in=request.user.user_dataroom__dataroom)
            try:
                count = queryset.count()
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page_index)
            except EmptyPage:
                return JSONResponse(SuccessResponse({'count': 0, 'data': []}))
            serializer = DataroomSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data, lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.admin_adddataroom'])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            projid = data.get('proj',None)
            if not projid:
                raise InvestError(20072,msg='proj 不能为空 int类型')
            try:
                proj = project.objects.get(id=projid,datasource=request.user.datasource,is_deleted=False)
            except project.DoesNotExist:
                raise InvestError(code=4002)
            if proj.projstatus_id < 4:
                raise InvestError(5003, msg='项目尚未终审发布')
            with transaction.atomic():
                publicdataroom = self.get_queryset().filter(proj=proj)
                if publicdataroom.exists():
                    responsedataroom = DataroomCreateSerializer(publicdataroom.first()).data
                else:
                    dataroomdata = {'proj': projid, 'datasource': request.user.datasource.id, 'createuser': request.user.id}
                    publicdataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                    if publicdataroomserializer.is_valid():
                        publicdataroom = publicdataroomserializer.save()
                        creatpublicdataroomdirectorywithtemplate(request.user, publicdataroomid=publicdataroom.id)
                        responsedataroom = publicdataroomserializer.data
                    else:
                        raise InvestError(code=20071, msg=publicdataroomserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(responsedataroom, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def addDataroom(self, request, *args, **kwargs):
        # 导数据专用   1 public
        try:
            data = request.data
            lang = request.GET.get('lang')
            projid = data.get('proj', None)
            if data.get('createuser', None) is None:
                createuser = request.user.id
            else:
                createuser = data.get('createuser')
            createdtime = data.pop('createdtime', None)
            if createdtime not in ['None', None, u'None', 'none']:
                createdtime = datetime.datetime.strptime(createdtime.encode('utf-8')[0:19], "%Y-%m-%d %H:%M:%S")
            else:
                createdtime = datetime.datetime.now()
            try:
                proj = project.objects.get(id=projid, datasource=request.user.datasource, is_deleted=False)
            except project.DoesNotExist:
                raise InvestError(code=4002)
            with transaction.atomic():
                dataroomdata = {'proj': projid, 'datasource': request.user.datasource.id, 'createuser': createuser,
                                'createdtime': createdtime}
                publicdataroom = self.get_queryset().filter(proj=proj)
                if publicdataroom.exists():
                    responsedic = DataroomCreateSerializer(publicdataroom.first()).data
                else:
                    publicdataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                    if publicdataroomserializer.is_valid():
                        publicdataroomserializer.save()
                        responsedic = publicdataroomserializer.data
                    else:
                        raise InvestError(code=20071, msg=publicdataroomserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(responsedic, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            serializer = DataroomdirectoryorfileSerializer(dataroomdirectoryorfile.objects.filter(is_deleted=False,dataroom=instance,isFile=False),many=True)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    #关闭/打开dataroom
    @loginTokenIsAvailable(['dataroom.admin_closedataroom'])
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.isClose = not instance.isClose
            instance.closeDate=datetime.datetime.now()
            instance.save()
            return JSONResponse(
                SuccessResponse(returnListChangeToLanguage(DataroomSerializer(instance).data)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.admin_deletedataroom'])
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            with transaction.atomic():
                instance.dataroom_directories.all().update(is_deleted=True, deletedtime=datetime.datetime.now())
                for fileOrDirectory in instance.dataroom_directories.all():
                    deleteInstance(fileOrDirectory, request.user)
                instance.is_deleted = True
                instance.deleteduser = request.user
                instance.deletedtime = datetime.datetime.now()
                instance.save()
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(DataroomSerializer(instance).data)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class DataroomdirectoryorfileView(viewsets.ModelViewSet):
    """
           list:dataroom文件或目录列表
           create:新建dataroom文件或目录
           update:移动目录或文件到目标位置
           destroy:删除dataroom文件或目录
        """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = dataroomdirectoryorfile.objects.all().filter(is_deleted=False)
    filter_fields = ('dataroom', 'parent','isFile')
    serializer_class = DataroomdirectoryorfileCreateSerializer
    Model = dataroomdirectoryorfile

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

    @loginTokenIsAvailable(['dataroom.admin_getdataroom',])
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang',None)
            dataroomid = request.GET.get('dataroom',None)
            if dataroomid is None:
                raise InvestError(code=20072,msg='dataroom 不能空')
            queryset = self.filter_queryset(self.get_queryset()).filter(datasource=self.request.user.datasource)
            count = queryset.count()
            serializer = DataroomdirectoryorfileSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.admin_adddataroom',])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            dataroomid = data.get('dataroom', None)
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            if data.get('parent', None):
                parentfile = self.get_object(data['parent'])
                if parentfile.isFile:
                    raise InvestError(7007, msg='非文件夹类型')
                if parentfile.dataroom_id != dataroomid:
                    raise InvestError(7011, msg='dataroom下没有该目录')
            with transaction.atomic():
                directoryorfileserializer = DataroomdirectoryorfileCreateSerializer(data=data)
                if directoryorfileserializer.is_valid():
                    directoryorfile = directoryorfileserializer.save()
                else:
                    raise InvestError(code=20071, msg='data有误_%s' % directoryorfileserializer.errors)
                if directoryorfile.parent is not None:
                    destquery = directoryorfile.parent.asparent_directories.exclude(pk=directoryorfile.pk).filter(is_deleted=False,orderNO__gte=directoryorfile.orderNO)
                    if destquery.exists():
                        destquery.update(orderNO = F('orderNO') + 1)
                #sendmessage_dataroomfileupdate(directoryorfile,directoryorfile.dataroom.investor,['sms','email','webmsg','app'],sender=request.user)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(DataroomdirectoryorfileSerializer(directoryorfile).data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.admin_changedataroom'])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            fileid = data.pop('id',None)
            if fileid is None:
                raise InvestError(2007,msg='fileid cannot be null')
            file = self.get_object(fileid)
            data['lastmodifyuser'] = request.user.id
            data['lastmodifytime'] = datetime.datetime.now()
            if data.get('dataroom', None):
                if file.dataroom_id != data.get('dataroom', None):
                    raise InvestError(7011, msg='不能移动到其他dataroom下')
            if data.get('parent', None):
                parentfile = self.get_object(data['parent'])
                if parentfile.dataroom != file.dataroom:
                    raise InvestError(7011, msg='不能移动到其他dataroom下')
                if parentfile.isFile:
                    raise InvestError(7007, msg='非文件夹类型')
            with transaction.atomic():
                directoryorfileserializer = DataroomdirectoryorfileUpdateSerializer(file,data=data)
                if directoryorfileserializer.is_valid():
                    directoryorfile = directoryorfileserializer.save()
                else:
                    raise InvestError(code=20071, msg='data有误_%s'% directoryorfileserializer.errors)
                if directoryorfile.parent is not None and data.get('orderNo', None):
                    destquery = directoryorfile.parent.asparent_directories.exclude(pk=directoryorfile.pk).filter(is_deleted=False,orderNO__gte=directoryorfile.orderNO)
                    if destquery.exist():
                        destquery.update(orderNO = F('orderNO')+ 1)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(directoryorfileserializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))



    @loginTokenIsAvailable(['dataroom.admin_deletedataroom',])
    def destroy(self, request, *args, **kwargs):
        try:
            filelist = request.data.get('filelist',None)
            if not isinstance(filelist,list) or not filelist:
                raise InvestError(code=20071,msg='need an id list')
            with transaction.atomic():
                for fileid in filelist:
                    instance = self.get_object(fileid)
                    if instance.isFile:
                        deleteInstance(instance, request.user)
                    else:
                        deleteDirectory(instance, request.user)
                return JSONResponse(SuccessResponse(filelist))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


class User_DataroomfileView(viewsets.ModelViewSet):
    """
           list:用户可见dataroom列表
           create:新建用户-dataroom关系
           retrieve:查看该dataroom用户可见文件列表
           update:编辑该dataroom用户可见文件列表
           destroy:减少用户可见dataroom
        """
    filter_backends = (filters.DjangoFilterBackend,)
    queryset = dataroom_User_file.objects.all().filter(is_deleted=False)
    filter_fields = ('dataroom', 'user')
    serializer_class = User_DataroomfileCreateSerializer
    Model = dataroom_User_file

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

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang',None)
            user = request.GET.get('user',None)
            if user:
                if user != request.user.id:
                    if request.user.has_perm('dataroom.admin_getdataroom'):
                        pass
                else:
                    raise InvestError(2009)
            queryset = self.filter_queryset(self.get_queryset()).filter(datasource=self.request.user.datasource,user=request.user)
            count = queryset.count()
            serializer = User_DataroomSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':returnListChangeToLanguage(serializer.data,lang)}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    @loginTokenIsAvailable()
    def retrieve(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang')
            instance = self.get_object()
            if request.user.has_perm('dataroom.admin_getdataroom'):
                serializerclass = User_DataroomfileSerializer
            elif request.user == instance.user:
                serializerclass = User_DataroomfileSerializer
            else:
                raise InvestError(code=2009)
            serializer = serializerclass(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.admin_adddataroom'])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            with transaction.atomic():
                user_dataroomserializer = User_DataroomfileCreateSerializer(data)
                if user_dataroomserializer.is_valid():
                    user_dataroomserializer.save()
                else:
                    raise InvestError(code=20071, msg='data有误_%s' % user_dataroomserializer.errors)
                return JSONResponse(SuccessResponse(user_dataroomserializer.data))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.admin_changedataroom'])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            user_dataroom = self.get_object()
            files = data.get('files', [])
            with transaction.atomic():
                user_dataroomserializer = User_DataroomfileCreateSerializer(user_dataroom, data={'files': files})
                if user_dataroomserializer.is_valid():
                    user_dataroomserializer.save()
                else:
                    raise InvestError(code=20071, msg='data有误_%s' % user_dataroomserializer.errors)
                return JSONResponse(SuccessResponse(returnDictChangeToLanguage(user_dataroomserializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.admin_deletedataroom'])
    def destroy(self, request, *args, **kwargs):
        try:
            user_dataroom = self.get_object()
            with transaction.atomic():
                user_dataroom.delete()
                return JSONResponse(SuccessResponse({'isDeleted':True}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


# dataroom 公共函数
# 创建public模板
def creatpublicdataroomdirectorywithtemplate(user, publicdataroomid):
    templatequery = publicdirectorytemplate.objects.all()
    topdirectories = templatequery.filter(parent=None)
    if topdirectories.exists():
        for directory in topdirectories:
            create_diractory(user, directoryname=directory.name, dataroom=publicdataroomid,
                             templatedirectoryID=directory.id, orderNO=directory.orderNO, parent=None)


def create_diractory(user, directoryname, dataroom, templatedirectoryID, orderNO, parent=None):
    directoryobj = dataroomdirectoryorfile(filename=directoryname, dataroom_id=dataroom, orderNO=orderNO,
                                           parent_id=parent, createdtime=datetime.datetime.now(), createuser_id=user.id,
                                           datasource_id=user.datasource_id)
    directoryobj.save()
    sondirectoryquery = publicdirectorytemplate.objects.filter(parent=templatedirectoryID)
    if sondirectoryquery.exists():
        for sondirectory in sondirectoryquery:
            create_diractory(user, directoryname=sondirectory.name, dataroom=dataroom,
                             templatedirectoryID=sondirectory.id, orderNO=sondirectory.orderNO, parent=directoryobj.id)


def pulishProjectCreateDataroom(proj, user):
    try:
        queryset = dataroom.objects.filter(is_deleted=False, datasource=user.datasource)
        publicdataroom = queryset.filter(proj=proj)
        if publicdataroom.exists():
            pass
        else:
            dataroomdata = {}
            dataroomdata['proj'] = proj.id
            dataroomdata['datasource'] = user.datasource_id
            dataroomdata['createuser'] = user.id
            publicdataroomserializer = DataroomCreateSerializer(data=dataroomdata)
            if publicdataroomserializer.is_valid():
                publicdataroom = publicdataroomserializer.save()
                creatpublicdataroomdirectorywithtemplate(user, publicdataroomid=publicdataroom.id)
    except Exception:
        logexcption(msg='public创建失败')
        pass


def deleteDirectory(instance, deleteuser):
    if not isinstance(instance, dataroomdirectoryorfile):
        raise InvestError(7007, msg='expect a dataroomdirectoryorfile type but get a %s type' % type(instance))
    if instance.is_deleted:
        raise InvestError(code=7002, msg='已删除，%s'%instance.id)
    else:
        filequery = instance.asparent_directories.filter(is_deleted=False)
        deleteInstance(instance, deleteuser)
        if filequery.count():
            for fileordirectoriey in filequery:
                deleteDirectory(fileordirectoriey, deleteuser)



def deleteInstance(instance, deleteuser):
    if instance.isFile:
        bucket = instance.bucket
        key = instance.key
        # instance.is_deleted = True
        # instance.deleteduser = deleteuser
        # instance.deletedtime = datetime.datetime.now()
        # instance.save()
        instance.delete()
        if not bucket or not key:
            pass
        else:
            ret, info = deleteqiniufile(bucket, key)
    else:
        instance.is_deleted = True
        instance.deleteduser = deleteuser
        instance.deletedtime = datetime.datetime.now()
        instance.save()
