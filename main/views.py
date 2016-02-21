from django.http import JsonResponse
from django.views.generic import View
from main.models import PresidingOfficer, PollingStation, POStatus, EVM, PollUpdate, LAC, SOSUpdate
from datetime import datetime
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
import math
from django.core.files.images import ImageFile
# Create your views here.


def degToRad(deg):
	return deg*(math.pi/180)


def getDistBetweenTwoPoints(lat1, long1, lat2, long2):
	R = 6371000 # Radius of Earth in meter
	dLat = degToRad(lat2-lat1) # degree to radian conversion
	dLong = degToRad(long2-long1)
	a = ((math.sin(dLat/2))**2) + ((math.sin(dLong/2))**2) * (math.cos(degToRad(lat1)) * math.cos(degToRad(lat2)))
	b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	c = R * b # distance in meter
	return c


class UpdatePOStatus(View):

	def post(self, request):
		flag = True
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			po_status = POStatus.objects.get(presiding_officer=presiding_officer)
			polling_station = presiding_officer.polling_station

			if "latitude" in request.POST and "longitude" in request.POST:
				po_status.last_latitude, po_status.last_longitude = po_status.current_latitude, po_status.current_longitude
				po_status.current_latitude, po_status.current_longitude = request.POST.get("latitude"), request.POST.get("longitude")
				po_status.save()

			if "received_evm" in request.POST:
				if request.POST.get("received_evm") == "true":
					po_status.received_evm = True
					po_status.save()
				else:
					flag = False
			elif "reached_polling_station" in request.POST:
				if request.POST.get("reached_polling_station") == "true":
					po_status.reached_polling_station = True
					po_status.save()
				else:
					flag = False
			elif "polling_station_condition" in request.POST:
				condition = int(request.POST.get("polling_station_condition"))
				# 0 for GOOD, 1 for BAD and 2 for DANGER
				if 0 <= condition <= 2:
					polling_station.condition = condition
					polling_station.save()
				else:
					flag = False
			elif "evm_number" in request.POST:
				if request.POST.get("evm_number") != "":
					try:
						evm = EVM()
						evm.polling_station = polling_station
						evm.unique_id = request.POST.get("evm_number")
						evm.save()
					except Exception:
						flag = False
				else:
					flag = False
			elif "sealed_evm" in request.POST:
				if request.POST.get("sealed_evm") == "true":
					po_status.sealed_evm = True
					po_status.save()
				else:
					flag = False
			elif "received_release" in request.POST:
				if request.POST.get("received_release") == "true":
					po_status.reached_polling_station = True
					po_status.save()
				else:
					flag = False
			elif "poll_starts" in request.POST:
				if request.POST.get("poll_starts") == "true":
					distance = getDistBetweenTwoPoints(polling_station.latitude, polling_station.longitude, po_status.current_latitude, po_status.current_longitude)
					if distance < 100.00:
						po_status.poll_starts = True
						po_status.save()
					else:
						flag = False
				else:
					flag = False
			elif "poll_ends" in request.POST:
				if request.POST.get("poll_ends") == "true":
					po_status.poll_ends = True
					po_status.save()
				else:
					flag = False
			elif "reached_dc" in request.POST:
				if request.POST.get("reached_dc") == "true":
					po_status.reached_dc = True
					po_status.save()
				else:
					flag = False
			else:
				flag = False

		except PresidingOfficer.DoesNotExist:
			flag = False
		except POStatus.DoesNotExist:
			flag = False
		except PollingStation.DoesNotExist:
			flag = False
		if flag:
			return JsonResponse({'result': 'ok'})
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(UpdatePOStatus, self).dispatch(*args, **kwargs)


class LoginPO(View):

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	def post(self, request):
		poid = request.POST.get('poid')
		psid = request.POST.get('psid')
		try:
			ps = PollingStation.objects.get(unique_id=psid)
			presiding_officer = PresidingOfficer.objects.get(polling_station=ps, username=poid)
			password = (psid+'@#'+poid+str(datetime.date(datetime.now()))).encode('utf-8')
			key = hashlib.sha256(password)
			presiding_officer.api_key = key.hexdigest()
			presiding_officer.save()

			if "latitude" in request.POST and "longitude" in request.POST:
				po_status = POStatus.objects.get(presiding_officer=presiding_officer)
				po_status.last_latitude, po_status.last_longitude = po_status.current_latitude, po_status.current_longitude
				po_status.current_latitude, po_status.current_longitude = request.POST.get("latitude"), request.POST.get("longitude")
				po_status.save()

			return JsonResponse({'result': 'ok', 'access_token': presiding_officer.api_key})
		except PresidingOfficer.DoesNotExist:
			return JsonResponse({'result': 'fail'})
		except PollingStation.DoesNotExist:
			return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(LoginPO, self).dispatch(*args, **kwargs)


class LogoutPO(View):

	def post(self, request):
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid)
			presiding_officer.api_key = ""
			presiding_officer.save()

			if "latitude" in request.POST and "longitude" in request.POST:
				po_status = POStatus.objects.get(presiding_officer=presiding_officer)
				po_status.last_latitude, po_status.last_longitude = po_status.current_latitude, po_status.current_longitude
				po_status.current_latitude, po_status.current_longitude = request.POST.get("latitude"), request.POST.get("longitude")
				po_status.save()
			return JsonResponse({'result': 'ok'})
		except PresidingOfficer.DoesNotExist:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(LogoutPO, self).dispatch(*args, **kwargs)


class UpdatePoll(View):

	def post(self, request):
		flag = True
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			polling_station = presiding_officer.polling_station
			if "total_voters" in request.POST:
				total_voters = int(request.POST.get("total_voters"))
				if total_voters > 0:
					polling_station.total_voters = total_voters
					polling_station.save()
				else:
					flag = False
			elif "current_voters" in request.POST:
				current_voters = int(request.POST.get("current_voters"))
				if current_voters > 0:
					poll_update = PollUpdate()
					poll_update.current_votes = current_voters
					poll_update.polling_station = polling_station
					poll_update.timestamp = datetime.now()
					poll_update.save()
				else:
					flag = False
			else:
				flag = False

			if "latitude" in request.POST and "longitude" in request.POST:
				po_status = POStatus.objects.get(presiding_officer=presiding_officer)
				po_status.last_latitude, po_status.last_longitude = po_status.current_latitude, po_status.current_longitude
				po_status.current_latitude, po_status.current_longitude = request.POST.get("latitude"), request.POST.get("longitude")
				po_status.save()

		except PresidingOfficer.DoesNotExist:
			flag = False
		except PollingStation.DoesNotExist:
			flag = False

		if flag:
			return JsonResponse({'result': 'ok'})
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(UpdatePoll, self).dispatch(*args, **kwargs)


class DashboardView(TemplateView):
	template_name = "dashboard.html"

	def get_context_data(self, **kwargs):
		context = super(DashboardView, self).get_context_data(**kwargs)
		po_status = POStatus.objects.all()
		poll_updates = PollUpdate.objects.order_by('timestamp')
		po_evm = len(POStatus.objects.filter(received_evm = True))
		po_ps = len(POStatus.objects.filter(reached_polling_station = True))
		context['all'] = po_status
		context['up'] = poll_updates
		context['no'] = po_evm
		context['ps'] = po_ps

		return context


class CheckEarlyStatus(View):

	def post(self, request):
		flag = True
		received_evm = "false"
		reached_polling_station = "false"
		evm_number = "false"
		poll_starts = "false"
		poll_ends = "false"
		sealed_evm = "false"
		received_release = "false"
		reached_dc = "false"
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			polling_station = presiding_officer.polling_station
			po_status = POStatus.objects.get(presiding_officer=presiding_officer)
			evm = EVM.objects.filter(polling_station=polling_station)

			if len(evm) > 0:
				evm_number = "true"
			if po_status.received_evm:
				received_evm = "true"
			if po_status.reached_polling_station:
				reached_polling_station = "true"
			if po_status.poll_starts:
				poll_starts = "true"
			if po_status.poll_ends:
				poll_ends = "true"
			if po_status.sealed_evm:
				sealed_evm = "true"
			if po_status.received_release:
				received_release = "true"
			if po_status.reached_dc:
				reached_dc = "true"

			if "latitude" in request.POST and "longitude" in request.POST:
				po_status.last_latitude, po_status.last_longitude = po_status.current_latitude, po_status.current_longitude
				po_status.current_latitude, po_status.current_longitude = request.POST.get("latitude"), request.POST.get("longitude")
				po_status.save()

		except PresidingOfficer.DoesNotExist:
			flag = False

		if flag:
			return JsonResponse({'result': 'ok', 'received_evm': received_evm, 'reached_polling_station': reached_polling_station, 'evm_number': evm_number, 'poll_starts': poll_starts, 'poll_ends': poll_ends, 'sealed_evm': sealed_evm, 'received_release': received_release, 'reached_dc': reached_dc})
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(CheckEarlyStatus, self).dispatch(*args, **kwargs)


class SOSUpdateView(View):

	def post(self, request):
		flag = True
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			polling_station = presiding_officer.polling_station
			if "message" in request.POST and "subject" in request.POST and "condition" in request.POST and "image" in request.FILES:
				subject = int(request.POST.get("subject"))
				condition = int(request.POST.get("condition"))
				if 0 <= subject <= 2 and 0 <= condition <= 2:
					sos = SOSUpdate()
					sos.polling_station = polling_station
					sos.subject = subject
					sos.message = request.POST.get("message")
					sos.condition = condition
					sos.image = ImageFile(request.FILES["image"])
					sos.save()
				else:
					flag = False
			else:
				flag = False

			if "latitude" in request.POST and "longitude" in request.POST:
				po_status = POStatus.objects.get(presiding_officer=presiding_officer)
				po_status.last_latitude, po_status.last_longitude = po_status.current_latitude, po_status.current_longitude
				po_status.current_latitude, po_status.current_longitude = request.POST.get("latitude"), request.POST.get("longitude")
				po_status.save()

		except PresidingOfficer.DoesNotExist:
			flag = False

		if flag:
			return JsonResponse({'result': 'ok'})
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(SOSUpdateView, self).dispatch(*args, **kwargs)


class AllEVMofPO(View):

	def post(self, request):
		flag = True
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		evms = []
		total_evms = 0
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			polling_station = presiding_officer.polling_station
			evm_objects = EVM.objects.values('unique_id').filter(polling_station=polling_station)
			for evm in evm_objects:
				evms.append(evm['unique_id'])

			total_evms = len(evms)

			if "latitude" in request.POST and "longitude" in request.POST:
				po_status = POStatus.objects.get(presiding_officer=presiding_officer)
				po_status.last_latitude, po_status.last_longitude = po_status.current_latitude, po_status.current_longitude
				po_status.current_latitude, po_status.current_longitude = request.POST.get("latitude"), request.POST.get("longitude")
				po_status.save()

		except PresidingOfficer.DoesNotExist:
			flag = False

		if flag:
			return JsonResponse({'result': 'ok', 'evms': evms, 'total_evms': total_evms})
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(AllEVMofPO, self).dispatch(*args, **kwargs)


class AllPollUpdateofPO(View):

	def post(self, request):
		flag = True
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		total_voters = 0
		current_count = 0
		current_voters = dict()
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			polling_station = presiding_officer.polling_station
			if polling_station.total_voters:
				total_voters = polling_station.total_voters
			poll_update = PollUpdate.objects.order_by('-timestamp').filter(polling_station=polling_station)

			if len(poll_update) > 0:
				current_count = len(poll_update)
				for pu in poll_update:
					if pu.timestamp.minute > 30:
						current_voters[(pu.timestamp.hour + 6) % 24] = pu.current_votes
					else:
						current_voters[(pu.timestamp.hour + 5) % 24] = pu.current_votes

		except PresidingOfficer.DoesNotExist:
			flag = False

		if flag:
			return JsonResponse({'result': 'ok', 'total_voters': total_voters, 'current_count': current_count, 'current_voters': current_voters})
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(AllPollUpdateofPO, self).dispatch(*args, **kwargs)
