#coding=utf-8
from django.shortcuts import render
# Create your views here.
from rest_framework import filters , viewsets
from rest_framework import status
from rest_framework.permissions import AllowAny

from MyUserSys.models import MyToken
from MyUserSys.myauth import JSONResponse
from org.models import organization
from org.serializer import OrgSerializer


class OrganizationView(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter,filters.DjangoFilterBackend,)
    # permission_classes = (AllowAny,)
    queryset = organization.objects.order_by('id')
    # queryset = MyUser.objects.filter(is_active=True).order_by('-id')
    filter_fields = ('id','name','orgcode','orgstatu',)
    search_fields = ('id','name','orgcode','orgstatu',)
    serializer_class = OrgSerializer

    def list(self, request, *args, **kwargs):
        token = MyToken.objects.get(key=request.META.get('HTTP_TOKEN'))
        if token.user or token.user.is_superuser or token.user.has_perm('usersys.change_myuser'):
            response = {
                'result': str(self.queryset),
                'error': None,
            }
            return JSONResponse(response)
        else:
            response = {
                'result': None,
                'error': '没有权限',
            }
            return JSONResponse(response,status=status.HTTP_403_FORBIDDEN)


        # if request.user and request.user.has_perm('org.getorg'):
        #     response = {
        #         'result': str(self.queryset),
        #         'error': None,
        #     }
        #     return JSONResponse(response)
        # else:
        #     response = {
        #         'result': None,
        #         'error': 'user with this phone already exists.',
        #     }
        #     return JSONResponse(response)