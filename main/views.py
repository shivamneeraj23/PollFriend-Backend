from django.http import JsonResponse
from django.views.generic import View
from main.models import PresidingOfficer, PollingStation, POStatus
from datetime import datetime
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Create your views here.


class UpdatePOStatus(View):

	def post(self, request):
		flag = True
		poid = request.POST.get('poid')
		access_token = request.POST.get('access_token')
		try:
			presiding_officer = PresidingOfficer.objects.get(username=poid, api_key=access_token)
			po_status = POStatus.objects.get(presiding_officer=presiding_officer)
			if "received_evm" in request.POST:
				if request.POST.get("received_evm") == "true":
					po_status.received_evm = True
					po_status.save()
			elif "reached_polling_station" in request.POST:
				if request.POST.get("reached_polling_station") == "true":
					po_status.reached_polling_station = True
					po_status.save()
			else:
				flag = False

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
			return JsonResponse({'result': 'ok', 'access_token': presiding_officer.api_key})
		except PresidingOfficer.DoesNotExist:
			return JsonResponse({'result': 'fail'})
		except PollingStation.DoesNotExist:
			return JsonResponse({'result': 'fail'})

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(LoginPO, self).dispatch(*args, **kwargs)

