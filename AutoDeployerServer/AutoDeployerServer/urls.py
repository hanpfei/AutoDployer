"""AutoDeployerServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from deploy import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^createConfig', views.createConfig),
    url(r'^listConfig', views.list_config),
    url(r'^deleteConfig', views.delete_config),
    url(r'^deploy/', views.deploy),
    url(r'^stop/', views.stop),
    url(r'^restart/', views.restart),
    url(r'^getlog', views.getlog),
]
