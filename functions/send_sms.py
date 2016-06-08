"""Send SMS
To send SMS using SMS API, to the list of mobile numbers
"""
from django.conf import settings
import requests
__author__ = "Wicklers"


def SendSMS(message, mobiles):
	"""Sends a message to the list of mobile numbers in mobiles list.
	:param message: Message text to be sent.
	:param mobiles: Python List, containing 10 digit mobile numbers.
	:return: None
	"""
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

