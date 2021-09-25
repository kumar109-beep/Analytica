from django.urls import path, include, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings

from . import datatable_handler

# import .views
urlpatterns = [

    path('contributors/', views.list, name='contributor_list'),

    re_path(r'^contributor/(?P<pk>\d+)/delete/$', views.delete, name='user_delete'),
	re_path(r'^contributor/(?P<pk>\d+)/update/$', views.update, name='user_update'),
    re_path(r'^contributor/create/$', views.create, name='user_create'),
    
    re_path(r'^profile/$', views.view_profile, name='view_profile'),
    re_path(r'^profile/edit/$', views.edit_profile, name='edit_profile'),

    re_path(r'^change_password/$', views.change_password, name='change_password'),


    path('edit_requests/', views.edit_requests, name='edit_requests'),

    path('edit_request_list/', datatable_handler.TestModelListJson.as_view(), name='edit_request_list'),

    # url(r'^my/datatable/data/$', login_required(OrderListJson.as_view()), name='order_list_json'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)