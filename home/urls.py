from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('default_page/', views.default_page, name='default_page'),
    path('about/', views.about, name='about'),
    path('bcpm_login/', views.bcpm_login, name="bcpm_login"),
    path('login/', views.loginUser, name='loginUser'),
    path('signup/', views.signup, name='signup'),
]