#coding=utf-8
import threading
import traceback

from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import F
from django.http import StreamingHttpResponse
from rest_framework import filters, viewsets

from dataroom.models import dataroom, dataroomdirectoryorfile, publicdirectorytemplate, dataroom_User_file
from dataroom.serializer import DataroomSerializer, DataroomCreateSerializer, DataroomdirectoryorfileCreateSerializer, \
    DataroomdirectoryorfileSerializer, DataroomdirectoryorfileUpdateSerializer, User_DataroomfileSerializer, \
    User_DataroomSerializer, User_DataroomfileCreateSerializer
from invest.settings import APILOG_PATH
from proj.models import project
from third.views.qiniufile import deleteqiniufile, downloadFileToPath
from utils.customClass import InvestError, JSONResponse, RelationFilter
from utils.sendMessage import sendmessage_dataroomfileupdate
from utils.somedef import file_iterator,  addWaterMarkToPdfFiles
from utils.util import returnListChangeToLanguage, loginTokenIsAvailable, \
    returnDictChangeToLanguage, catchexcption, SuccessResponse, InvestErrorResponse, ExceptionResponse, \
    logexcption, checkrequesttoken
import datetime
from django_filters import FilterSet
import os
import shutil

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
    search_fields = ('proj__projtitleC', 'proj__projtitleE', 'proj__supportUser__usernameC')
    filter_class = DataroomFilter
    serializer_class = DataroomSerializer

    def get_object(self):
        lookup_url_kwarg = 'pk'
        try:
            obj = dataroom.objects.get(id=self.kwargs[lookup_url_kwarg], is_deleted=False)
        except dataroom.DoesNotExist:
            raise InvestError(code=6002,msg='timeline with this "%s" is not exist' % self.kwargs[lookup_url_kwarg])
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
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
            return JSONResponse(SuccessResponse(returnListChangeToLanguage(serializer.data, lang)))
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
                instance.dataroom_users.all().update(is_deleted=True)
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

    @loginTokenIsAvailable(['dataroom.downloadDataroom'])
    def makeDataroomAllFilesZip(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            userid = request.GET.get('user',None)
            watermarkcontent = request.GET.get('water',None)
            qs = instance.dataroom_directories.all().filter(is_deleted=False)
            rootpath = APILOG_PATH['dataroomFilePath'] + '/' + 'dataroom_%s%s'%(str(instance.id), '_%s'%userid if userid else '')
            startMakeDataroomZip(qs, rootpath , instance,userid,watermarkcontent)
            return JSONResponse(SuccessResponse('dataroom_%s%s.zip'%(str(instance.id), '_%s'%userid if userid else '')))
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.downloadDataroom'])
    def checkZipStatus(self, request, *args, **kwargs):
        try:
            path = request.GET.get('path', None)
            rootpath = APILOG_PATH['dataroomFilePath'] + '/' + path
            direcpath = APILOG_PATH['dataroomFilePath'] + '/' + path
            direcpath = direcpath.replace('.zip', '')
            if os.path.exists(rootpath):
                response = JSONResponse(SuccessResponse({'code': 8005, 'msg': '压缩文件已备好'}))
            else:
                if os.path.exists(direcpath):
                    response = JSONResponse(SuccessResponse({'code': 8004, 'msg': '压缩中'}))
                else:
                    response = JSONResponse(SuccessResponse({'code': 8002, 'msg': '文件不存在'}))
            return response
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

    @loginTokenIsAvailable(['dataroom.downloadDataroom'])
    def downloadDataroomZip(self, request, *args, **kwargs):
        try:
            user =checkrequesttoken(request.GET.get('token',None))
            if not user.has_perm('dataroom.downloadDataroom'):
                raise InvestError(2009)
            path = request.GET.get('path',None)
            rootpath = APILOG_PATH['dataroomFilePath'] + '/' + path
            direcpath = APILOG_PATH['dataroomFilePath'] + '/' + path
            direcpath = direcpath.replace('.zip','')
            if os.path.exists(rootpath):
                fn = open(rootpath, 'rb')
                response = StreamingHttpResponse(file_iterator(fn))
                response['Content-Type'] = 'application/octet-stream'
                response["content-disposition"] = 'attachment;filename=%s' % path
                os.remove(rootpath)
                if os.path.exists(direcpath):
                    shutil.rmtree(direcpath)
            else:
                if os.path.exists(direcpath):
                    response = JSONResponse(SuccessResponse({'code':8004, 'msg': '压缩中'}))
                else:
                    response = JSONResponse(SuccessResponse({'code':8002, 'msg': '文件不存在'}))
            return response
        except InvestError as err:
            return JSONResponse(InvestErrorResponse(err))
        except Exception:
            catchexcption(request)
            return JSONResponse(ExceptionResponse(traceback.format_exc().split('\n')[-2]))

def startMakeDataroomZip(file_qs,path, dataroominstance,userid=None,watermarkcontent=None):
    class downloadAllDataroomFile(threading.Thread):
        def __init__(self, qs, path):
            self.qs = qs
            self.path = path
            threading.Thread.__init__(self)

        def run(self):
            directory_qs = self.qs.filter(isFile=False)
            makeDirWithdirectoryobjs(directory_qs, self.path)
            if userid:
                try:
                    userfile_qs = dataroom_User_file.objects.get(dataroom=dataroominstance,user_id=userid).files.all()
                except dataroom_User_file.DoesNotExist:
                    raise InvestError(2007,msg='未找到符合条件的dataroom')
                # file_qs = file_qs.filter(id__in=userfile_qs)
            else:
                userfile_qs = self.qs.filter(isFile=True)
            filepaths = []
            for file_obj in userfile_qs:
                path = getPathWithFile(file_obj, self.path)
                savepath = downloadFileToPath(key=file_obj.realfilekey, bucket=file_obj.bucket, path=path)
                if savepath:
                    print savepath
                    filetype = path.split('.')[-1]
                    if filetype in ['pdf', u'pdf']:
                        filepaths.append(path)
            addWaterMarkToPdfFiles(filepaths, watermarkcontent)
            import zipfile
            zipf = zipfile.ZipFile(self.path+'.zip', 'w')
            pre_len = len(os.path.dirname(self.path))
            for parent, dirnames, filenames in os.walk(self.path):
                for filename in filenames:
                    pathfile = os.path.join(parent, filename)
                    arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
                    zipf.write(pathfile, arcname)
            zipf.close()
    d = downloadAllDataroomFile(file_qs, path)
    d.start()
    # d.join()

def makeDirWithdirectoryobjs(directory_objs ,rootpath):
    if os.path.exists(rootpath):
        shutil.rmtree(rootpath)
    os.makedirs(rootpath)
    for file_obj in directory_objs:
        try:
            path = getPathWithFile(file_obj,rootpath)
            os.makedirs(path)
        except OSError:
            pass

def getPathWithFile(file_obj,rootpath,currentpath=None):
    if currentpath is None:
        currentpath = file_obj.filename
    if file_obj.parent is None:
        return rootpath + '/' + currentpath
    else:
        currentpath = file_obj.parent.filename + '/' + currentpath
        return getPathWithFile(file_obj.parent, rootpath, currentpath)


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
            raise InvestError(code=8888)
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
                    deleteInstance(instance, request.user)
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
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend,)
    queryset = dataroom_User_file.objects.all().filter(is_deleted=False,dataroom__isClose=False,dataroom__is_deleted=False)
    filter_fields = ('dataroom', 'user')
    search_fields = ('dataroom__proj__projtitleC','dataroom__proj__projtitleE')
    serializer_class = User_DataroomfileCreateSerializer
    Model = dataroom_User_file

    def get_object(self,pk=None):
        if pk:
            try:
                obj = self.queryset.get(id=pk, is_deleted=False)
            except self.Model.DoesNotExist:
                raise InvestError(code=7002, msg='dataroom-user with this "%s" is not exist' % pk)
        else:
            try:
                obj = self.queryset.get(id=self.kwargs['pk'], is_deleted=False)
            except self.Model.DoesNotExist:
                raise InvestError(code=7002,msg='dataroom-user with this （"%s"） is not exist' % self.kwargs['pk'])
        if obj.datasource != self.request.user.datasource:
            raise InvestError(code=8888)
        return obj

    @loginTokenIsAvailable()
    def list(self, request, *args, **kwargs):
        try:
            lang = request.GET.get('lang', 'cn')
            user = request.GET.get('user',None)
            if request.user.has_perm('dataroom.admin_getdataroom'):
                filters = {'datasource':self.request.user.datasource}
            else:
                filters = {'datasource':self.request.user.datasource, 'user':request.user.id}
                if user:
                    if user != request.user.id:
                        raise InvestError(2009)
            queryset = self.filter_queryset(self.get_queryset()).filter(**filters)
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
                data['datasource'] = request.user.datasource_id
                data['createuser'] = request.user.id
                user_dataroomserializer = User_DataroomfileCreateSerializer(data=data)
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
                sendmessage_dataroomfileupdate(user_dataroom, user_dataroom.user,
                                               ['sms', 'email', 'webmsg', 'app'], sender=request.user)
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


def deleteInstance(instance, deleteuser):
    if instance.is_deleted:
        raise InvestError(code=7002, msg='%s不存在，已被删除'%instance.id)
    if instance.isFile:
        bucket = instance.bucket
        key = instance.key
        realkey = instance.realfilekey
        instance.delete()
        deleteqiniufile(bucket, key)
        deleteqiniufile(bucket, realkey)
    else:
        filequery = instance.asparent_directories.filter(is_deleted=False)
        if filequery.count():
            for fileordirectoriey in filequery:
                deleteInstance(fileordirectoriey, deleteuser)
        instance.is_deleted = True
        instance.deleteduser = deleteuser
        instance.deletedtime = datetime.datetime.now()
        instance.save()
