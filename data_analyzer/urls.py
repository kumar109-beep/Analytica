from django.urls import path
from . import views

urlpatterns = [

    path('data_analyzer/', views.analyzer, name='analyzer'),
    path('form_builder/', views.form_builder, name='form_builder'),


    

]