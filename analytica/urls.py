"""analytica URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

static_path = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
media_path = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from rest_framework.authtoken import views



urlpatterns = [
	path('', include('home.urls')),
    path('tracking/', include('tracking.urls')),
    path('tools/', include('data_analyzer.urls')),
    path('dashboard/', include('admin_panel.urls')),
    path('user-management/', include('user_management.urls')),
    path('survey/', include('survey.urls')),
    path('core_admin/', admin.site.urls),
    path('pc/', include('django.contrib.auth.urls')),
    
    #API Based Services
    path('chartGenerate/', include('chartGenerate.urls')),
    path('dataframe/', include('dataframe.urls')),

    path('client/', include('client.urls')),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api-token-auth/', views.obtain_auth_token)
]  +static_path+media_path



from django.conf.urls import (
handler400, handler403, handler404, handler500
)

# handler400 = 'admin_panel.views.admin_panel.bad_request'
# handler403 = 'admin_panel.views.admin_panel.permission_denied'
handler404 = 'admin_panel.views.admin_view.page_not_found'
# handler500 = 'admin_panel.views.admin_panel.server_error'

