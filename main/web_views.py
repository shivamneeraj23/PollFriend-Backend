from main.models import *
from django.views.generic.base import TemplateView
# Create your views here.


class DashboardView(TemplateView):
	template_name = "dashboard.html"

	def get_context_data(self, **kwargs):
		context = super(DashboardView, self).get_context_data(**kwargs)
		po_status = POStatus.objects.all()
		poll_updates = PollUpdate.objects.order_by('timestamp')
		po_evm = len(POStatus.objects.filter(received_evm = True))
		po_ps = len(POStatus.objects.filter(reached_polling_station = True))
		poll_starts = len(POStatus.objects.filter(poll_starts = True))
		poll_ends = len(POStatus.objects.filter(poll_ends = True))
		sealed_evm = len(POStatus.objects.filter(sealed_evm = True))
		received_release = len(POStatus.objects.filter(received_release = True))
		reached_dc = len(POStatus.objects.filter(reached_dc = True))


		context['all'] = po_status
		context['up'] = poll_updates
		context['received_evm'] = po_evm
		context['reached_polling_station'] = po_ps
		context['poll_starts'] = poll_starts
		context['poll_ends'] = poll_ends
		context['sealed_evm'] = sealed_evm
		context['received_release'] = received_release
		context['reached_dc'] = reached_dc

		return context


class MessageView(TemplateView):
	template_name = "messaging.html"

	def get_context_data(self, **kwargs):
		context = super(MessageView, self).get_context_data(**kwargs)
		po_status = POStatus.objects.all()
		context['po_status'] = po_status

		return context


class AdminLogin(TemplateView):
	template_name = "login.html"