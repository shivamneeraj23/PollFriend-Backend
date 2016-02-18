"""evmts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from main.views import *

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^recieved_evm/', RecievedEvm.as_view() , name = 'recieved_evm'),
    url(r'^reached_ps/' , ReachedPS.as_view() , name = 'reached_ps'),
    url(r'^polling_cond/', PollingCond.as_view() , name = 'polling_cond')
]
