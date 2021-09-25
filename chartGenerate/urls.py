from django.urls import path, re_path
from . views import ChartConfList, ChartConfDetail


# import .views
urlpatterns = [
    path('configurations/',  ChartConfList.as_view()),
    path('configuration/<int:pk>/', ChartConfDetail.as_view()),
]





