from django.http import JsonResponse
from django.views.generic import View
from main.models import *
from datetime import datetime
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from functions.haversine_formula import getDistBetweenTwoPoints
from django.core.files.images import ImageFile
import requests
import json
from django.conf import settings

# Create your views here.


def SavePOLocation(latitude, longitude, presiding_officer):
	po_location = POLocation()
	po_location.presiding_officer = presiding_officer
	po_location.latitude, po_location.longitude = latitude, longitude
	po_location.save()


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
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

			if "received_evm" in request.POST:
				if request.POST.get("received_evm") == "true":
					po_status.received_evm = True
					po_status.received_evm_timestamp = datetime.now()
					po_status.save()
				else:
					flag = False
			elif "reached_polling_station" in request.POST:
				if request.POST.get("reached_polling_station") == "true":
					po_status.reached_polling_station = True
					po_status.reached_polling_station_timestamp = datetime.now()
					po_status.save()
				else:
					flag = False
			elif "polling_station_condition" in request.POST:
				condition = int(request.POST.get("polling_station_condition"))
				# 0 for GOOD, 1 for OK and 2 for BAD
				if 0 <= condition <= 2:
					polling_station.condition = condition + 1
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
					po_status.sealed_evm_timestamp = datetime.now()
					po_status.save()
				else:
					flag = False
			elif "received_release" in request.POST:
				if request.POST.get("received_release") == "true":
					po_status.received_release = True
					po_status.received_release_timestamp = datetime.now()
					po_status.save()
				else:
					flag = False
			elif "mock_poll_starts" in request.POST:
				if request.POST.get("mock_poll_starts") == "true":
					latitude = request.POST.get("latitude")
					longitude = request.POST.get("longitude")
					distance = getDistBetweenTwoPoints(polling_station.latitude, polling_station.longitude, latitude, longitude)
					if distance < 200.00:
						po_status.mock_poll_starts = True
						po_status.mock_poll_starts_timestamp = datetime.now()
						po_status.save()
					else:
						flag = False
				else:
					flag = False
			elif "mock_poll_ends" in request.POST:
				if request.POST.get("mock_poll_ends") == "true":
					po_status.mock_poll_ends = True
					po_status.mock_poll_ends_timestamp = datetime.now()
					po_status.save()
				else:
					flag = False
			elif "mock_poll_resetted" in request.POST:
				if request.POST.get("mock_poll_resetted") == "true":
					po_status.mock_poll_resetted = True
					po_status.mock_poll_resetted_timestamp = datetime.now()
					po_status.save()
				else:
					flag = False
			elif "poll_starts" in request.POST:
				if request.POST.get("poll_starts") == "true":
					latitude = request.POST.get("latitude")
					longitude = request.POST.get("longitude")
					distance = getDistBetweenTwoPoints(polling_station.latitude, polling_station.longitude, latitude, longitude)
					if distance < 200.00:
						po_status.poll_starts = True
						po_status.poll_starts_timestamp = datetime.now()
						po_status.save()
					else:
						flag = False
				else:
					flag = False
			elif "poll_ends" in request.POST:
				if request.POST.get("poll_ends") == "true":
					po_status.poll_ends = True
					po_status.poll_ends_timestamp = datetime.now()
					po_status.save()
				else:
					flag = False
			elif "reached_dc" in request.POST:
				if request.POST.get("reached_dc") == "true":
					po_status.reached_dc = True
					po_status.reached_dc_timestamp = datetime.now()
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
			presiding_officer.last_login = datetime.now()
			presiding_officer.save()

			if "latitude" in request.POST and "longitude" in request.POST:
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

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
			presiding_officer.last_logout = datetime.now()
			presiding_officer.save()

			if "latitude" in request.POST and "longitude" in request.POST:
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

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
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

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


class CheckEarlyStatus(View):

	def post(self, request):
		flag = True
		received_evm = "false"
		reached_polling_station = "false"
		polling_station_condition = "false"
		total_voters = "false"
		evm_number = "false"
		poll_starts = "false"
		poll_ends = "false"
		mock_poll_starts = "false"
		mock_poll_ends = "false"
		mock_poll_resetted = "false"
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

			if polling_station.condition:
				polling_station_condition = polling_station.condition - 1
			if polling_station.total_voters:
				total_voters = "true"
			if len(evm) > 0:
				evm_number = "true"
			if po_status.received_evm:
				received_evm = "true"
			if po_status.reached_polling_station:
				reached_polling_station = "true"
			if po_status.mock_poll_starts:
				mock_poll_starts = "true"
			if po_status.mock_poll_resetted:
				mock_poll_resetted = "true"
			if po_status.mock_poll_ends:
				mock_poll_ends = "true"
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
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

		except PresidingOfficer.DoesNotExist:
			flag = False

		if flag:
			response = {'result': 'ok', 'received_evm': received_evm, 'reached_polling_station': reached_polling_station, 'evm_number': evm_number, 'mock_poll_starts': mock_poll_starts, 'mock_poll_ends': mock_poll_ends, 'mock_poll_resetted': mock_poll_resetted, 'poll_starts': poll_starts, 'poll_ends': poll_ends, 'sealed_evm': sealed_evm, 'received_release': received_release, 'reached_dc': reached_dc, 'polling_station_condition': polling_station_condition, 'total_voters': total_voters}
			return JsonResponse(response)
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(CheckEarlyStatus, self).dispatch(*args, **kwargs)


class SOSUpdateView(View):

	def post(self, request):
		flag = False
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			polling_station = presiding_officer.polling_station
			sos = SOSUpdate()
			sos.polling_station = polling_station
			if "image" in request.FILES:
				sos.image = ImageFile(request.FILES["image"])
				flag = True
			if "message" in request.POST:
				sos.message = request.POST.get("message")
				flag = True
			if "subject" in request.POST:
				try:
					subject = int(request.POST.get("subject"))
					if 0 <= subject <= 2:
						sos.subject = subject + 1
						flag = True
				except ValueError:
					flag = False
			if "condition" in request.POST:
				try:
					condition = int(request.POST.get("condition"))
					if 0 <= condition <= 2:
						sos.condition = condition
						flag = True
				except ValueError:
					flag = False

			sos.save()
			# Multi-Cast SOS to all WEB ADMINS
			# Set header
			headers = dict()
			headers['Authorization'] = "key="+settings.GCM_AUTH_KEY
			headers['Content-Type'] = "application/json"
			# get all admin web devices
			web_devices = WebDevice.objects.filter()
			device_keys = []
			for wd in web_devices:
				device_keys.append(wd.device_key)
			# Set POST data
			data = dict()
			data['registration_ids'] = device_keys
			# JSON serialize the dict data-type
			data = json.dumps(data)
			# initiate the request
			r = requests.post(settings.GCM_URL, data=data, headers=headers)
			if r.status_code == 200:
				pass

			if "latitude" in request.POST and "longitude" in request.POST:
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

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
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

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

			if "latitude" in request.POST and "longitude" in request.POST:
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

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


class UploadPSImage(View):

	def post(self, request):
		flag = False
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			polling_station = presiding_officer.polling_station
			if "image" in request.FILES:
				ps_image = PSImage()
				ps_image.polling_station = polling_station
				ps_image.image = ImageFile(request.FILES["image"])
				ps_image.save()
				flag = True
			if "latitude" in request.POST and "longitude" in request.POST:
				SavePOLocation(request.POST.get("latitude"), request.POST.get("longitude"), presiding_officer)

		except PresidingOfficer.DoesNotExist:
			pass

		if flag:
			return JsonResponse({'result': 'ok'})
		else:
			return JsonResponse({'result': 'fail'})

	def get(self, request):
		return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(UploadPSImage, self).dispatch(*args, **kwargs)
