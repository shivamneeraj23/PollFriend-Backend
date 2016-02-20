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
	url(r'^login/$', LoginPO.as_view(), name="loginPO"),
	url(r'^po_status/$', UpdatePOStatus.as_view(), name="UpdatePOStatus"),
	url(r'^logout/$', LogoutPO.as_view(), name="logoutPO"),
	url(r'^poll_update/$', UpdatePoll.as_view(), name="PollUpdate"),
	url(r'^test/$' , Test.as_view(), name = "Test")
]
