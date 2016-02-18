from django.http import JsonResponse
from django.views.generic import View
from main.models import PresidingOfficer, PollingStation
from datetime import datetime
import hashlib
# Create your views here.

class RecievedEvm(View):

	def post(self, request):

		return JsonResponse({'result' : 'ok' })
	def get(self , request):
		return JsonResponse({'result' : 'ok'})


class ReachedPS(View):

	def post(self , request):

		return JsonResponse({'result' : 'ok'})

class PollingCond(View):

	def post(self , request):

		if cond == 'good':
			return JsonResponse({'result' : 'good'})
		else:
			return JsonResponse({'result' : 'ok'})

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
