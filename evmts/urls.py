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
from main.api_views import *
from main.web_views import *

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^login/$', LoginPO.as_view(), name="loginPO"),
	url(r'^po_status/$', UpdatePOStatus.as_view(), name="UpdatePOStatus"),
	url(r'^logout/$', LogoutPO.as_view(), name="logoutPO"),
	url(r'^poll_update/$', UpdatePoll.as_view(), name="PollUpdate"),
	url(r'^home/$', DashboardView.as_view(), name="DashboardView"),
	url(r'^check_status/$', CheckEarlyStatus.as_view(), name="checkEarlyStatus"),
	url(r'^sos_update/$', SOSUpdateView.as_view(), name="SOSUpdate"),
	url(r'^get_evms/$', AllEVMofPO.as_view(), name="AllEVM"),
	url(r'^check_poll_update/$', AllPollUpdateofPO.as_view(), name="AllPollUpdatesPO"),
	url(r'^upload_ps_image/$', UploadPSImage.as_view(), name="PSImages"),
	url(r'^messages/$', MessageView.as_view(), name='MessagingView'),
	url(r'^$', AdminLogin.as_view(), name='AdminLoginView'),
	url(r'^register_web_device/$', RegisterWebDevice.as_view(), name='RegisterWebDevice'),
]
