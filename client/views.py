from rest_framework import permissions
from rest_framework import generics

from django.contrib.auth.models import User, Group, Permission
from . serializers import ClientSerializer, RoleSerializer, PermissionSerializer



class ClientList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = ClientSerializer

class ClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ClientSerializer



class RoleList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer

class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer



class PermissionList(generics.ListCreateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class PermissionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer