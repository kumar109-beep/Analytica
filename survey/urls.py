from django.urls import path, re_path
from . import views
from admin_panel.views import admin_view

urlpatterns = [

    re_path(r'^analytics/(?P<survey_name>\w+)/$', views.analytics, name='survey_analytics'),
    # re_path(r'^records/(?P<survey_name>\w+)/$', views.records, name='survey_records'),
    re_path(r'^records/(?P<profile>\w+)/$', admin_view.master_record , name='survey_records'),
    re_path(r'^gis/(?P<survey_name>\w+)/$', views.records, name='survey_gis'),


    re_path(r'^load_survey/$', views.load_survey, name='load_survey'),


    re_path(r'^load_geography/$', views.getGeoList, name='load_geography'),


    



]