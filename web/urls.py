from django.conf.urls import url
from web.views import *

urlpatterns = [
	url(r'^$', AdminLogin.as_view(), name='AdminLoginView'),
	url(r'^home/$', DashboardView.as_view(), name="DashboardView"),
	url(r'^messages/$', MessageView.as_view(), name='Message'),
	url(r'^messages/inbox/$', MessageInboxView.as_view(), name='MessageInbox'),
	url(r'^messages/sent/$', MessageSentView.as_view(), name='MessageSent'),
	url(r'^register_web_device/$', RegisterWebDevice.as_view(), name='RegisterWebDevice'),
	url(r'^polling-station/view/$', PollingStationListView.as_view(), name='PollingStation'),
	url(r'^get_sos_notification/$', GetSOSNotification.as_view(), name='GetSOSNotification'),
	url(r'^polling-station/add/$', PollingStationListAddView.as_view(), name='PollingStationAdd'),
	url(r'^presiding-officer/view/$', PresidingOfficerListView.as_view(), name='PresidingOfficer'),
	url(r'^presiding-officer/add/$', PresidingOfficerListAddView.as_view(), name='PresidingOfficerAdd'),
	url(r'^polling-station/(?P<ps_id>\d+)/$', PollingStationView.as_view() , name = 'PollingStationView'),
	url(r'^presiding-officer/(?P<pk>\d+)/$', PresidingOfficerView.as_view() , name = 'PresidingOfficerView'),
	url(r'^messages/compose/$', MessageComposeView.as_view(), name='MessageCompose'),
	url(r'^admin-logout/$', AdminLogout.as_view(), name='AdminLogout'),
	url(r'^download_csv/$', DownloadCSV.as_view(), name='DownloadCSV'),
]