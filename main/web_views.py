from main.models import *
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse_lazy
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


class MessageView(RedirectView):
	url = reverse_lazy("MessageInbox")


class MessageInboxView(TemplateView):
	template_name = "messages.html"

	def get_context_data(self, **kwargs):
		context = super(MessageInboxView, self).get_context_data(**kwargs)
		sos = SOSUpdate.objects.order_by('-timestamp').filter()
		context['sos_messages'] = sos

		return context


class MessageSentView(TemplateView):
	template_name = "messages.html"

	def get_context_data(self, **kwargs):
		context = super(MessageInboxView, self).get_context_data(**kwargs)
		sos = SOSUpdate.objects.order_by('-timestamp').filter()
		context['sos_messages'] = sos

		return context


class AdminLogin(TemplateView):
	template_name = "login.html"


class RegisterWebDevice(View):
	def post(self, request):
		flag = False
		user = request.user
		if user.is_authenticated():
			try:
				web_device = WebDevice.objects.get(user=user)
			except WebDevice.DoesNotExist:
				web_device = WebDevice()
				web_device.user = user
			web_device.device_key = request.POST.get('device_key')
			web_device.save()
			flag = True
		else:
			return JsonResponse({'result': 'user_prob'})
		if flag:
			return JsonResponse({'result': 'ok'})
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(RegisterWebDevice, self).dispatch(*args, **kwargs)

