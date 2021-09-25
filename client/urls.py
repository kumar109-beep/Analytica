from django.urls import path, re_path
from . views import ClientList, ClientDetail, RoleList, RoleDetail, PermissionList, PermissionDetail


# import .views
urlpatterns = [
    path('users/',  ClientList.as_view()),
    path('user/<int:pk>/', ClientDetail.as_view()),


    path('roles/', RoleList.as_view()),
    path('role/<int:pk>/', RoleDetail.as_view()),


    path('permissions/',  PermissionList.as_view()),
    path('permission/<int:pk>/', PermissionDetail.as_view()),


    # path('edits',  Frame_edit_requestList.as_view()),
    # path('edit/<int:pk>', Frame_edit_requestDetail.as_view()),
]