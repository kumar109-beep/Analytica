from rest_framework import permissions
from rest_framework import generics

from . models import Chartconfig
from . serializers import ChartconfigSerializer

class ChartConfList(generics.ListCreateAPIView):
    queryset = Chartconfig.objects.all()
    serializer_class = ChartconfigSerializer

class ChartConfDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chartconfig.objects.all()
    serializer_class = ChartconfigSerializer