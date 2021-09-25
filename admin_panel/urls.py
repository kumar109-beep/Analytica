from django.urls import path, re_path
from .views import admin_view, core_functions

# import .views
urlpatterns = [

    path('', admin_view.index, name='index'),

    re_path(r'^generate_chart_data/(?P<profile>\w+)/$', admin_view.generate_chart_data, name='generate_chart_data'),
    re_path(r'^analytics/(?P<profile>\w+)/$', admin_view.analytics, name='analytics'),

    re_path(r'^records_ajax/(?P<profile>\w+)/$', admin_view.master_record_ajax, name='master_record_ajax'),
    re_path(r'^records/(?P<profile>\w+)/$', admin_view.master_record, name='master_record'),

    # re_path(r'^records_ajax/(?P<profile>)', admin_view.master_record_ajax, name='master_record_ajax'),
    # re_path(r'^records/(?P<profile>)', admin_view.master_record, name='master_record'),

    re_path(r'^gis/(?P<profile>\w+)/$', admin_view.master_gis, name='gis'),
    re_path(r'^get_geojson/(?P<profile>\w+)/$', admin_view.get_geojson, name='get_geojson'),


    re_path(r'^reports/', admin_view.master_reports, name='reports'),
    
    
    path('get_frame_heads/', admin_view.get_frame_heads, name='get_frame_heads'),
    path('get_head_vals/', admin_view.get_head_vals, name='get_head_vals'),

    
    re_path(r'^prepare_redis/(?P<frame_name>\w+)/$', core_functions.prepare_redis, name='prepare_redis'),


    # re_path(r'^stream/', admin_view.large_csv, name='stream'),


    re_path(r'^request_edit/', admin_view.request_edit, name='stream'),

    re_path(r'^charts/', admin_view.make_charts_ui, name='make_charts_ui'),
    
    

]
