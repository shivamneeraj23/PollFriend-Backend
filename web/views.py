from main.models import *
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse_lazy
from django.views.generic.list import ListView
from django.shortcuts import render
import json
from django.conf import settings
import requests
from functions.send_sms import SendSMS
from django.views.decorators.cache import never_cache
from django.db.models import Sum
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import loader, Context
# Create your views here.


class DashboardView(TemplateView):
	template_name = "dashboard.html"

	def get_context_data(self, **kwargs):
		context = super(DashboardView, self).get_context_data(**kwargs)
		po_status = POStatus.objects.all().select_related()
		poll_updates = PollUpdate.objects.order_by('polling_station', '-timestamp', '-time_field').filter().select_related()
		polling_station = PollingStation.objects.all()
		ps_cv = dict()
		ps_percentage = dict()
		po_evm = po_ps = poll_starts = poll_ends = sealed_evm = mock_poll = received_release = reached_dc = 0
		total_voters = current_voters = 0
		good = ok = bad = 0
		total_9 = total_11 = total_1 = total_3 = total_5 = total_last = 0
		for ps in polling_station:
			ps_cv[ps.unique_id] = 0
			ps_percentage[ps.unique_id] = 0.00
			if ps.total_voters:
				total_voters += ps.total_voters
			if ps.condition:
				if ps.condition == 1:
					good += 1
				elif ps.condition == 2:
					ok += 1
				elif ps.condition == 3:
					bad += 1

		pu = PollUpdate.objects.values('current_votes', 'polling_station__unique_id', 'polling_station__total_voters').order_by('polling_station', '-timestamp', '-time_field').filter().distinct('polling_station')
		for p in pu:
			current_voters += p['current_votes']
			p_cv = p['current_votes']
			ps_cv[p['polling_station__unique_id']] = p_cv
			p_tv = p['polling_station__total_voters']
			try:
				ps_percentage[p['polling_station__unique_id']] = round(((p_cv/p_tv)*100), 2)
			except TypeError:
				ps_percentage[p['polling_station__unique_id']] = 0.00

		last_ps = None
		last_time_field = 0

		for p in poll_updates:
			if p.time_field == last_time_field and p.polling_station == last_ps:
				continue
			if p.time_field == 9:
				total_9 += p.current_votes
			elif p.time_field == 11:
				total_11 += p.current_votes
			elif p.time_field == 1:
				total_1 += p.current_votes
			elif p.time_field == 3:
				total_3 += p.current_votes
			elif p.time_field == 5:
				total_5 += p.current_votes
			elif p.time_field == 6:
				total_last += p.current_votes

			last_time_field = p.time_field
			last_ps = p.polling_station

		pl = POLocation.objects.order_by('presiding_officer', '-timestamp').filter().distinct('presiding_officer').select_related()

		for po in po_status:
			if po.received_evm:
				po_evm += 1
			if po.reached_polling_station:
				po_ps += 1
			if po.poll_starts:
				poll_starts += 1
			if po.poll_ends:
				poll_ends += 1
			if po.sealed_evm:
				sealed_evm += 1
			if po.received_release:
				received_release += 1
			if po.reached_dc:
				reached_dc += 1
			if po.mock_poll_ends:
				mock_poll += 1

		if total_voters and current_voters:
			percentage = round(((current_voters/total_voters)*100), 2)
		else:
			percentage = 0.00

		total_logged_in = len(PresidingOfficer.objects.filter(~Q(last_login=None)))
		presiding_officer_no = len(po_status)

		context['all'] = po_status
		context['up'] = poll_updates
		context['received_evm'] = po_evm
		context['reached_polling_station'] = po_ps
		context['poll_starts'] = poll_starts
		context['poll_ends'] = poll_ends					
		context['sealed_evm'] = sealed_evm
		context['received_release'] = received_release
		context['reached_dc'] = reached_dc
		context['good'] = good
		context['ok'] = ok
		context['bad'] = bad
		context['presiding_officer_no'] = presiding_officer_no
		context['mock_poll'] = mock_poll
		context['percentage'] = percentage
		context['active_po'] = total_logged_in
		context['inactive_po'] = presiding_officer_no - total_logged_in
		context['po_locations'] = pl
		context['ps_cv'] = ps_cv
		context['ps_percentage'] = ps_percentage
		try:
			context['total_9'] = round(((total_9/total_voters)*100), 2)
			context['total_11'] = round(((total_11/total_voters)*100), 2)
			context['total_1'] = round(((total_1/total_voters)*100), 2)
			context['total_3'] = round(((total_3/total_voters)*100), 2)
			context['total_5'] = round(((total_5/total_voters)*100), 2)
			context['total_last'] = round(((total_last/total_voters)*100), 2)
		except ZeroDivisionError:
			context['total_9'] = 0.00
			context['total_11'] = 0.00
			context['total_1'] = 0.00
			context['total_3'] = 0.00
			context['total_5'] = 0.00
			context['total_last'] = 0.00
		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(DashboardView, self).dispatch(*args, **kwargs)


class MessageView(RedirectView):
	url = reverse_lazy("MessageInbox")


class MessageInboxView(TemplateView):
	template_name = "messages.html"

	def get_context_data(self, **kwargs):
		context = super(MessageInboxView, self).get_context_data(**kwargs)
		sos = SOSUpdate.objects.order_by('-timestamp').filter()
		context['sos_messages'] = list(sos)

		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(MessageInboxView, self).dispatch(*args, **kwargs)


class MessageSentView(TemplateView):
	template_name = "messages_sent.html"

	def get_context_data(self, **kwargs):
		context = super(MessageSentView, self).get_context_data(**kwargs)
		context['messages'] = Message.objects.order_by('-count_id').filter().distinct('count_id')
		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(MessageSentView, self).dispatch(*args, **kwargs)


class AdminLogin(View):
	template_name = "login.html"

	def post(self, request):
		flag = False
		user = request.user
		if user.is_authenticated():
			flag = True
		else:
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(username=username, password=password)
			if user:
				if user.is_active:
					login(request, user)
					flag = True
				else:
					flag = False
			else:
				flag = False

		if flag:
			if "next" in request.POST:
				return HttpResponseRedirect(request.POST.get("next"))
			else:
				return HttpResponseRedirect(reverse_lazy("DashboardView"))
		else:
			return render(request, self.template_name, {'login_failed': True})

	def get(self, request):
		user = request.user
		if user.is_authenticated():
			return HttpResponseRedirect(reverse_lazy("DashboardView"))
		else:
			return render(request, self.template_name, {'login_failed': False})

	@method_decorator(never_cache)
	def dispatch(self, *args, **kwargs):
		return super(AdminLogin, self).dispatch(*args, **kwargs)


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


class PollingStationListView(ListView):
	template_name = "pollingstation_list.html"
	model = PollingStation

	def get_context_data(self, **kwargs):
		context = super(PollingStationListView, self).get_context_data(**kwargs)
		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(PollingStationListView, self).dispatch(*args, **kwargs)


class GetSOSNotification(View):
	notif_id = 0

	def get(self, request):
		if 'last_notif_id' in request.COOKIES:
			notif_id = request.COOKIES.get('last_notif_id') + 1
			sos = SOSUpdate.objects.get(id=notif_id)
		else:
			sos = SOSUpdate.objects.order_by('-timestamp').filter()[0]
			notif_id = sos.id

		data = dict()
		data['notification'] = dict()
		if sos.get_condition_display() and sos.get_subject_display():
			data['notification']['title'] = sos.polling_station.name + " " + sos.get_subject_display() + " " + sos.get_condition_display()
		elif sos.get_condition_display():
			data['notification']['title'] = sos.polling_station.name + " " + sos.get_condition_display()
		elif sos.get_subject_display():
			data['notification']['title'] = sos.polling_station.name + " " + sos.get_subject_display()
		else:
			data['notification']['title'] = sos.polling_station.name + " SOS Alert!"

		if sos.message:
			data['notification']['message'] = sos.message
		else:
			data['notification']['message'] = "Please click here to check the details."

		data['notification']['notif_id'] = notif_id

		return JsonResponse(data)


class PollingStationListAddView(ListView):
	template_name = "pollingstation_add.html"
	model = PollingStation

	def get_context_data(self, **kwargs):
		context = super(PollingStationListAddView, self).get_context_data(**kwargs)
		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(PollingStationListAddView, self).dispatch(*args, **kwargs)


class PresidingOfficerListView(View):
	template_name = "presidingofficer_list.html"

	def get(self, request):
		object_list = None
		context = dict()
		po_filter = None
		if "sortBy" in request.GET:
			sort_by = request.GET.get("sortBy")
			if sort_by == "loggedIn":
				object_list = PresidingOfficer.objects.filter(~Q(last_login=None)).select_related()
				po_filter = "Logged In"
			elif sort_by == "notLoggedIn":
				object_list = PresidingOfficer.objects.filter(Q(last_login=None)).select_related()
				po_filter = "Not Logged In"
			else:
				po_filter = "All"
				object_list = PresidingOfficer.objects.filter().select_related()
		else:
			po_filter = "All"
			object_list = PresidingOfficer.objects.filter().select_related()
		context['po_filter'] = po_filter
		context['object_list'] = object_list
		return render(request, self.template_name, context)

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(PresidingOfficerListView, self).dispatch(*args, **kwargs)


class PresidingOfficerListAddView(ListView):
	template_name = "presidingofficer_add.html"
	model = PresidingOfficer

	def get_context_data(self, **kwargs):
		context = super(PresidingOfficerListAddView, self).get_context_data(**kwargs)
		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(PresidingOfficerListAddView, self).dispatch(*args, **kwargs)


class PollingStationView(TemplateView):
	
	template_name = "pollingstationview.html"

	def get_context_data(self , **kwargs):
		context = super(PollingStationView, self).get_context_data(**kwargs)
		ps = PollingStation.objects.get(id=int(self.kwargs['ps_id']))
		ps_images = PSImage.objects.order_by('-timestamp').filter(polling_station=ps)
		officer = PresidingOfficer.objects.get(polling_station = ps)
		poll_updates = PollUpdate.objects.order_by('-timestamp').filter(polling_station=ps)
		context['polling_station'] = ps
		context['ps_images'] = ps_images
		context['officer'] = officer
		context['poll_updates'] = poll_updates
		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(PollingStationView, self).dispatch(*args, **kwargs)


class PresidingOfficerView(TemplateView):
	
	template_name = "presidingofficerview.html"

	def get_context_data(self , **kwargs):
		context = super(PresidingOfficerView, self).get_context_data(**kwargs)
		po = PresidingOfficer.objects.get(id=int(self.kwargs['pk']))
		po_status = POStatus.objects.get(presiding_officer = po)
		# ps_images = PSImage.objects.order_by('-timestamp').filter(polling_station=ps)
		# officer = PresidingOfficer.objects.get(polling_station = ps)
		# poll_updates = PollUpdate.objects.order_by('-timestamp').filter(polling_station=ps)
		context['presiding_officer'] = po
		context['po_status'] = po_status
		# context['ps_images'] = ps_images
		# context['officer'] = officer
		# context['poll_updates'] = poll_updates
		return context

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(PresidingOfficerView, self).dispatch(*args, **kwargs)
		

class MessageComposeView(View):
	template_name = "messages_compose.html"

	def get(self, request):
		if request.user.has_perm("main.add_message"):
			presiding_officers = None
			if "sortBy" in request.GET:
				sort_by = request.GET.get("sortBy")
				if sort_by == "loggedIn":
					presiding_officers = PresidingOfficer.objects.filter(~Q(last_login=None)).select_related()
				elif sort_by == "notLoggedIn":
					presiding_officers = PresidingOfficer.objects.filter(Q(last_login=None)).select_related()
				else:
					presiding_officers = PresidingOfficer.objects.filter().select_related()
			else:
				presiding_officers = PresidingOfficer.objects.filter().select_related()
			context = dict()
			context['presiding_officers'] = presiding_officers
			if request.is_ajax():
				reply = dict()
				for po in presiding_officers:
					reply[po.id] = dict()
					reply[po.id]["id"] = po.id
					reply[po.id]["full_name"] = po.full_name
					reply[po.id]["username"] = po.username
					reply[po.id]["ps_unique_id"] = po.polling_station.unique_id
					reply[po.id]["ps_name"] = po.polling_station.name

				return JsonResponse(reply)
			return render(request, self.template_name, context)
		else:
			return HttpResponseRedirect(reverse_lazy("MessageInbox"))

	def post(self, request):
		if request.user.has_perm("main.add_message"):
			presiding_officers = PresidingOfficer.objects.filter()
			context = dict()
			context['presiding_officers'] = presiding_officers
			presiding_officers = request.POST.getlist('presiding_officers[]')
			message = request.POST.get('message')
			if len(presiding_officers) == 0 and not message:
				context['success'] = False
				context['message_missing'] = True
				context['po_missing'] = True
				return render(request, self.template_name, context)

			if len(presiding_officers) == 0:
				context['success'] = False
				context['message_missing'] = False
				context['po_missing'] = True
				return render(request, self.template_name, context)

			if not message:
				context['success'] = False
				context['message_missing'] = True
				context['po_missing'] = False
				return render(request, self.template_name, context)

			count = 1
			msg = Message.objects.order_by('-count_id').filter()
			if msg:
				msg = msg[0]
				count = msg.count_id + 1

			mobiles = []
			gcm_devices = []
			for po in presiding_officers:
				PO = PresidingOfficer.objects.get(id=po)

				if PO.device_key:
					gcm_devices.append(PO.device_key)
				if PO.mobile:
					mobiles.append(PO.mobile)
				if PO.second_mobile:
					mobiles.append(PO.second_mobile)

				msg = Message()
				msg.user = request.user
				msg.count_id = count
				msg.message = message
				msg.presiding_officer = PO
				msg.save()

			notification = dict()
			notification['title'] = "Broadcast Message"
			notification['body'] = message
			# Multi-Cast SOS to all WEB ADMINS
			# Set header
			headers = dict()
			headers['Authorization'] = "key="+settings.GCM_AUTH_KEY
			headers['Content-Type'] = "application/json"
			# Set POST data
			data = dict()
			data['registration_ids'] = gcm_devices
			data['notification'] = notification
			data['data'] = notification

			# JSON serialize the dict data-type
			data = json.dumps(data)
			# initiate the request
			if len(gcm_devices) > 0:
				r = requests.post(settings.GCM_URL, data=data, headers=headers)
				if r.status_code == 200:
					pass
			# Send SMS notification
			if len(mobiles) > 0:
				r = SendSMS(message, mobiles)
				if r.status_code == 200:
					pass

			presiding_officers = PresidingOfficer.objects.filter()
			context = dict()
			context['presiding_officers'] = presiding_officers
			context['success'] = True
			return render(request, self.template_name, context)
		else:
			return HttpResponseRedirect(reverse_lazy("MessageInbox"))

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(MessageComposeView, self).dispatch(*args, **kwargs)


class AdminLogout(View):

	def post(self, request):
		logout(request)
		return HttpResponseRedirect(reverse_lazy("AdminLoginView"))

	def get(self, request):
		logout(request)
		return HttpResponseRedirect(reverse_lazy("AdminLoginView"))


class DownloadCSV(View):
	
	def get(self, request):
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="CurrentData.csv"'
		all_po = POStatus.objects.order_by('presiding_officer__polling_station').select_related()
		t = loader.get_template('excel_data_dumps.txt')
		c = Context({'data': all_po,})
		response.write(t.render(c))
		return response 

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(DownloadCSV, self).dispatch(*args, **kwargs)