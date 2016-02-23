from django import template
from main.models import PollUpdate, POLocation

register = template.Library()


@register.simple_tag
def current_vote_percentage(polling_station):
	pu = PollUpdate.objects.order_by('-timestamp').filter(polling_station=polling_station)
	percentage = 0
	if len(pu) > 0 and polling_station.total_voters:
		pu = pu[0]
		percentage = (pu.current_votes * 100)/polling_station.total_voters
	return percentage


@register.simple_tag
def get_current_location(presiding_officer):
	po_location = POLocation.objects.order_by('-timestamp').filter(presiding_officer=presiding_officer)
	lat, long = None, None

	if po_location:
		po_location = po_location[0]
		lat, long = float(po_location.latitude), float(po_location.longitude)

	return [lat, long]


