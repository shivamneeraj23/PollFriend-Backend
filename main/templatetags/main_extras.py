from django import template
from main.models import PollUpdate, POLocation
from functions.haversine_formula import getDistBetweenTwoPoints

register = template.Library()


@register.simple_tag
def current_vote_percentage(polling_station):
	pu = PollUpdate.objects.order_by('-timestamp').filter(polling_station=polling_station)
	percentage = 0
	if len(pu) > 0 and polling_station.total_voters:
		pu = pu[0]
		percentage = (pu.current_votes * 100) / polling_station.total_voters
	return round(percentage, 2)


@register.simple_tag
def current_voters(polling_station):
	pu = PollUpdate.objects.order_by('-timestamp').filter(polling_station=polling_station)
	current_votes = 0
	if len(pu) > 0 and polling_station.total_voters:
		pu = pu[0]
		current_votes = pu.current_votes
	return current_votes


@register.simple_tag
def get_current_location(presiding_officer):
	po_location = POLocation.objects.order_by('-timestamp').filter(presiding_officer=presiding_officer)
	lat, long = 0.0, 0.0

	if po_location:
		po_location = po_location[0]
		lat, long = float(po_location.latitude), float(po_location.longitude)

	return [lat, long]


@register.simple_tag
def get_percentage(total, current):
	if total and current:
		return round((current * 100) / total, 2)
	else:
		return 0


@register.inclusion_tag('sidebar.html', takes_context=True)
def get_sidebar(context):
	request = context['request']
	parent_page = request.path.split('/')[1]
	return {'page': request.path, 'parent': parent_page}


@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)


@register.simple_tag
def get_current_distance(presiding_officer):
	po_location = POLocation.objects.order_by('-timestamp').filter(presiding_officer=presiding_officer)
	lat, long = 0.0, 0.0

	if po_location:
		po_location = po_location[0]
		lat, long = float(po_location.latitude), float(po_location.longitude)

	if lat == 0.0 and long == 0.0:
		return "----"

	ps_lat, ps_long = presiding_officer.polling_station.latitude, presiding_officer.polling_station.latitude
	distance = getDistBetweenTwoPoints(lat, long, ps_lat, ps_long)

	if distance >= 1000:
		return str(round((distance / 1000.00), 2)) + " KM"
	else:
		return str(distance) + " Meter"
