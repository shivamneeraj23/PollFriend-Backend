from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from django.http import JsonResponse
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
