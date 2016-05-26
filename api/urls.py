from django.conf.urls import url
from api.views import *

urlpatterns = [
	url(r'^login/$', LoginPO.as_view(), name="loginPO"),
	url(r'^po_status/$', UpdatePOStatus.as_view(), name="UpdatePOStatus"),
	url(r'^logout/$', LogoutPO.as_view(), name="logoutPO"),
	url(r'^poll_update/$', UpdatePoll.as_view(), name="PollUpdate"),
	url(r'^check_status/$', CheckEarlyStatus.as_view(), name="checkEarlyStatus"),
	url(r'^sos_update/$', SOSUpdateView.as_view(), name="SOSUpdate"),
	url(r'^get_evms/$', AllEVMofPO.as_view(), name="AllEVM"),
	url(r'^check_poll_update/$', AllPollUpdateofPO.as_view(), name="AllPollUpdatesPO"),
	url(r'^upload_ps_image/$', UploadPSImage.as_view(), name="PSImages"),
	url(r'^register_mobile_device/$', RegisterMobileDevice.as_view(), name='RegisterMobileDevice'),
	url(r'^get_other_details/$', GetOtherDetails.as_view(), name='GetOtherDetails'),
	url(r'^sos_acknowledgement/$', SOSAcknowledgement.as_view(), name='SOSAcknowledgement'),
	url(r'^emergency_contacts/$', EmergencyContacts.as_view(), name='EmergencyContacts'),
]