from django.conf import settings
import requests


def SendSMS(message, mobiles):
	if len(mobiles) > 0 and message:
		data = dict()
		data['key'] = settings.SMS_KEY
		data['type'] = "text"
		data['senderid'] = settings.SMS_SENDER
		data['msg'] = message
		mobiles = ','.join(list(map(str, mobiles)))
		data['contacts'] = mobiles
		r = requests.get(settings.SMS_URL, params=data)
		return r

