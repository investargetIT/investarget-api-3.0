#coding=utf-8
import traceback

from django.core.paginator import Paginator, EmptyPage
from django.db import models
from django.db import transaction
from django.db.models import F
from django.db.models import Q,QuerySet, FieldDoesNotExist
from django.db.models.fields.reverse_related import ForeignObjectRel
from rest_framework import filters, viewsets

from dataroom.models import dataroom, dataroomdirectoryorfile, publicdirectorytemplate
from dataroom.serializer import DataroomSerializer, DataroomCreateSerializer, DataroomdirectoryorfileCreateSerializer, \
    DataroomdirectoryorfileSerializer, DataroomdirectoryorfileUpdateSerializer
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
    isPublic = RelationFilter(filterstr='isPublic', lookup_method='in')
    proj = RelationFilter(filterstr='proj', lookup_method='in')
    investor = RelationFilter(filterstr='investor', lookup_method='in')
    trader = RelationFilter(filterstr='trader', lookup_method='in')
    isClose = RelationFilter(filterstr='isClose', lookup_method='in')
    user = RelationFilter(filterstr='user', lookup_method='in')
    class Meta:
        model = dataroom
        fields = ('proj', 'investor', 'trader', 'isClose','user','isPublic' , 'supportuser')

class DataroomView(viewsets.ModelViewSet):
    """
       list:dataroom列表
       create:新建dataroom
       update:关闭dataroom
       destroy:删除dataroom
    """
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend,)
    queryset = dataroom.objects.all().filter(is_deleted=False)
    search_fields = ('proj__projtitleC', 'investor__usernameC', 'trader__usernameC', 'user__usernameC', 'proj__supportUser__usernameC')
    filter_class = DataroomFilter
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
            userid = request.GET.get('user',None)
            isPublic = request.GET.get('isPublic',None)
            if not page_size:
                page_size = 10
            if not page_index:
                page_index = 1
            queryset = self.filter_queryset(self.get_queryset())
            if not userid and not isPublic:
                queryset = queryset.filter(isPublic=False).exclude(trader__isnull=True,investor__isnull=True)
            sort = request.GET.get('sort')
            if sort not in ['True', 'true', True, 1, 'Yes', 'yes', 'YES', 'TRUE']:
                queryset = queryset.order_by('-lastmodifytime', '-createdtime')
            else:
                queryset = queryset.order_by('lastmodifytime', 'createdtime')
            if request.user.has_perm('dataroom.admin_getdataroom'):
                queryset = queryset
            else:
                if not isPublic:
                    queryset = queryset.filter(Q(user=request.user) | Q(trader=request.user) | Q(investor=request.user))
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
            if proj.projstatus_id < 4:
                raise InvestError(5003, msg='项目尚未终审发布')
            with transaction.atomic():
                responselist = []
                dataroomdata = {'proj':projid,'datasource':request.user.datasource.id,'createuser':request.user.id}
                projdataroom = self.get_queryset().filter(proj=proj,user_id=proj.supportUser_id,isPublic=False)
                publicdataroom = self.get_queryset().filter(proj=proj, isPublic=True)
                if projdataroom.exists():
                    responselist.append(DataroomCreateSerializer(projdataroom.first()).data)
                else:
                    dataroomdata['user'] = proj.supportUser_id
                    dataroomdata['isPublic'] = False
                    supportordataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                    if supportordataroomserializer.is_valid():
                        supportdataroom = supportordataroomserializer.save()
                        add_perm('dataroom.user_getdataroom', supportdataroom.user, supportdataroom)
                        add_perm('dataroom.user_changedataroom', supportdataroom.user, supportdataroom)
                        responselist.append(supportordataroomserializer.data)
                    else:
                        raise InvestError(code=20071, msg=supportordataroomserializer.errors)
                if publicdataroom.exists():
                    responselist.append(DataroomCreateSerializer(publicdataroom.first()).data)
                else:
                    dataroomdata['user'] = proj.supportUser_id
                    dataroomdata['isPublic'] = True
                    publicdataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                    if publicdataroomserializer.is_valid():
                        publicdataroom = publicdataroomserializer.save()
                        creatpublicdataroomdirectorywithtemplate(request.user, publicdataroomid=publicdataroom.id)
                        responselist.append(publicdataroomserializer.data)
                    else:
                        raise InvestError(code=20071, msg=publicdataroomserializer.errors)
                if not ispublic:
                    investordataroom = self.get_queryset().filter(proj=proj, user_id=investorid, trader_id=traderid,investor_id=investorid)
                    if investordataroom.exists():
                        responselist.append(DataroomCreateSerializer(investordataroom.first()).data)
                    else:
                        dataroomdata['user'] = None
                        dataroomdata['isPublic'] = False
                        dataroomdata['investor'] = investorid
                        dataroomdata['trader'] = traderid
                        investordataroomserializer = DataroomCreateSerializer(data=dataroomdata)
                        if investordataroomserializer.is_valid():
                            investordata = investordataroomserializer.save()
                            userlist = [investordata.investor, investordata.trader, investordata.createuser, investordata.proj.makeUser,
                                        investordata.proj.takeUser, investordata.proj.supportUser]
                            for user in userlist:
                                add_perm('dataroom.user_getdataroom', user, investordata)
                            add_perm('dataroom.user_changedataroom', investordata.investor, investordata)
                            responselist.append(investordataroomserializer.data)
                        else:
                            raise InvestError(code=20071,msg=investordataroomserializer.errors)
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(responselist, lang)))
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
                serializerclass = DataroomSerializer
            elif request.user.has_perm('dataroom.user_getdataroom', instance):
                serializerclass = DataroomSerializer
            else:
                raise InvestError(code=2009)
            serializer = serializerclass(instance)
            return JSONResponse(SuccessResponse(returnDictChangeToLanguage(serializer.data, lang)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))


    #关闭/打开dataroom
    @loginTokenIsAvailable()
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            traderid = data.get('trader', None)
            investorid = data.get('investor', None)
            projid = data.get('proj', None)
            isClose = data.get('isClose',False)
            if isClose in ['True', 1, '1', 'true', 'TRUE']:
                isClose = True
            else:
                isClose = False
            if not data or not traderid or not investorid or not projid:
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
            dataroomquery.update(isClose=isClose,closeDate=datetime.datetime.now())
            return JSONResponse(
                SuccessResponse(returnListChangeToLanguage(DataroomSerializer(dataroomquery, many=True).data)))
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
            elif request.user.has_perm('dataroom.user_deletedataroom',dataroomquery.get(investor_id=investorid)):
                pass
            else:
                raise InvestError(code=2009)
            with transaction.atomic():
                for instance in dataroomquery:
                    instance.dataroom_directories.all().update(is_deleted=True,deletedtime=datetime.datetime.now())
                    for fileOrDirectory in instance.dataroom_directories.all():
                        if fileOrDirectory.isFile and fileOrDirectory.key:
                            deleteqiniufile(fileOrDirectory.bucket, fileOrDirectory.key)
                    instance.is_deleted = True
                    instance.deleteduser = request.user
                    instance.deletedtime = datetime.datetime.now()
                    instance.save()
                return JSONResponse(SuccessResponse(returnListChangeToLanguage(DataroomSerializer(dataroomquery,many=True).data)))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

#创建public模板
def creatpublicdataroomdirectorywithtemplate(user,publicdataroomid):
    templatequery = publicdirectorytemplate.objects.all()
    topdirectories = templatequery.filter(parent=None)
    if topdirectories.exists():
        for directory in topdirectories:
            create_diractory(user,directoryname=directory.name,dataroom=publicdataroomid,templatedirectoryID=directory.id,orderNO=directory.orderNO,parent=None)
    #创建public模板
def create_diractory(user,directoryname,dataroom,templatedirectoryID,orderNO,parent=None):
    directoryobj = dataroomdirectoryorfile(filename=directoryname, dataroom_id=dataroom,orderNO=orderNO,parent_id=parent,createdtime=datetime.datetime.now(),createuser_id=user.id,datasource_id=user.datasource_id)
    directoryobj.save()
    sondirectoryquery = publicdirectorytemplate.objects.filter(parent=templatedirectoryID)
    if sondirectoryquery.exists():
        for sondirectory in sondirectoryquery:
            create_diractory(user,directoryname=sondirectory.name,dataroom=dataroom,templatedirectoryID=sondirectory.id,orderNO=sondirectory.orderNO,parent=directoryobj.id)

def pulishProjectCreateDataroom(proj,user):
    try:
        queryset = dataroom.objects.filter(is_deleted=False)
        projdataroom = queryset.filter(proj=proj, user_id=proj.supportUser_id, isPublic=False)
        publicdataroom = queryset.filter(proj=proj, isPublic=True)
        if projdataroom.exists():
            pass
        else:
            dataroomdata = {}
            dataroomdata['user'] = proj.supportUser_id
            dataroomdata['isPublic'] = False
            supportordataroomserializer = DataroomCreateSerializer(data=dataroomdata)
            if supportordataroomserializer.is_valid():
                supportdataroom = supportordataroomserializer.save()
                add_perm('dataroom.user_getdataroom', supportdataroom.user, supportdataroom)
                add_perm('dataroom.user_changedataroom', supportdataroom.user, supportdataroom)
        if publicdataroom.exists():
            pass
        else:
            dataroomdata = {}
            dataroomdata['user'] = proj.supportUser_id
            dataroomdata['isPublic'] = True
            publicdataroomserializer = DataroomCreateSerializer(data=dataroomdata)
            if publicdataroomserializer.is_valid():
                publicdataroom = publicdataroomserializer.save()
                creatpublicdataroomdirectorywithtemplate(user, publicdataroomid=publicdataroom.id)
    except Exception:
        logexcption()
        pass


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
            dataroomid = request.GET.get('dataroom',None)
            queryset = self.filter_queryset(self.get_queryset())
            if dataroomid and isinstance(dataroomid,(int,str,unicode)):
                dataroomobj = self.get_dataroom(dataroomid)
                if dataroomobj.isPublic:
                    pass
                elif request.user.has_perm('dataroom.admin_getdataroom'):
                    pass
                elif request.user.has_perm('dataroom.user_getdataroom', dataroomobj):
                    pass
                else:
                    raise InvestError(code=2009)
            else:
                raise InvestError(code=20072,msg='dataroom 不能空')
            count = queryset.count()
            serializer = DataroomdirectoryorfileSerializer(queryset, many=True)
            return JSONResponse(SuccessResponse({'count':count,'data':serializer.data,}))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable()
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            lang = request.GET.get('lang')
            dataroomid = data.get('dataroom', None)
            if dataroomid:
                dataroomobj = self.get_dataroom(dataroomid)
                if dataroomobj.isClose:
                    raise InvestError(7012)
                elif request.user.has_perm('dataroom.admin_adddataroom'):
                    pass
                elif request.user.has_perm('dataroom.user_adddataroomfile', dataroomobj):
                    pass
                else:
                    raise InvestError(code=2009)
            else:
                raise InvestError(code=20072)
            data['createuser'] = request.user.id
            data['datasource'] = request.user.datasource.id
            if data.get('parent', None):
                parentfile = self.get_object(data['parent'])
                if parentfile.isFile:
                    raise InvestError(7007, msg='非文件夹类型')
                if self.checkDirectoryIsShadow(parentfile):
                    raise InvestError(7009, msg='不能把文件f复制到复制体文件夹内')
                if parentfile.dataroom_id != dataroomid:
                    raise InvestError(7011, msg='dataroom下没有该目录')
            if data.get('isShadow', None):
                if data['shadowdirectory'] is None:
                    raise InvestError(2007,msg='\"shadowdirectory\" 不能为空')
                shadowdirectory = self.get_object(data['shadowdirectory'])
                if shadowdirectory.isShadow:
                    raise InvestError(7009,msg='影子目录不能复制')
                if shadowdirectory.dataroom_id == dataroomid:
                    raise InvestError(7011,msg='文件复制不能再同一个dataroom下')
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
                sendmessage_dataroomfileupdate(directoryorfile,directoryorfile.dataroom.investor,['sms','email','webmsg','app'],sender=request.user)
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
            if data.get('dataroom', None):
                if file.dataroom_id != data.get('dataroom', None):
                    raise InvestError(7011, msg='不能移动到其他dataroom下')
            if data.get('parent', None):
                parentfile = self.get_object(data['parent'])
                if parentfile.dataroom != file.dataroom:
                    raise InvestError(7011, msg='不能移动到其他dataroom下')
                if parentfile.isFile:
                    raise InvestError(7007, msg='非文件夹类型')
                if self.checkDirectoryIsShadow(parentfile):
                    raise InvestError(7009, msg='不能把文件移入复制体文件夹内')
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
                    elif request.user.has_perm('dataroom.user_deletedataroom', instance.dataroom):
                        pass
                    else:
                        raise InvestError(code=2009, msg='没有权限')
                    if instance.isFile:
                        self.deleteInstance(instance, request.user)
                    else:
                        self.deleteDirectory(instance,request.user)
                return JSONResponse(SuccessResponse(filelist))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    def deleteDirectory(self,instance,deleteuser):
        if not isinstance(instance,dataroomdirectoryorfile):
            raise InvestError(7007,msg='expect a dataroomdirectoryorfile type but get a %s type'%type(instance))
        if instance.is_deleted:
            raise InvestError(code=7002)
        else:
            if instance.isShadow:
                self.deleteInstance(instance, deleteuser)
            else:
                filequery = instance.asparent_directories.filter(is_deleted=False)
                self.deleteInstance(instance, deleteuser)
                if filequery.count():
                    for fileordirectoriey in filequery:
                       self.deleteDirectory(fileordirectoriey, deleteuser)


    def deleteInstance(self,instance,deleteuser):
        if instance.isFile:
            instance.is_deleted = True
            instance.deleteduser = deleteuser
            instance.deletedtime = datetime.datetime.now()
            instance.save()
            if instance.isShadow:
                pass
            else:
                if not instance.bucket or not instance.key:
                    pass
                else:
                    deleteqiniufile(instance.bucket, instance.key)
        else:
            instance.is_deleted = True
            instance.deleteduser = deleteuser
            instance.deletedtime = datetime.datetime.now()
            instance.save()


    def checkDirectoryIsShadow(self,directory):
        if directory.isShadow:
            return True
        else:
            subDirs = directory.asparent_directories.filter(is_deleted=False)
            if subDirs.exists():
                for subDir in subDirs:
                    self.checkDirectoryIsShadow(subDir)

    def gerDirectoryAllSubDirOrFile(self,directory):
        qs = directory.asparent_directories.filter(is_deleted=False, isShadow=False)
        for dir in qs:
            if dir.isFile:
                pass
            else:
                subqs = self.gerDirectoryAllSubDirOrFile(dir)
                qs = (qs | subqs).distinct()
        return qs

