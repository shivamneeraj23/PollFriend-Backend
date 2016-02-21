from django import template
from main.models import PollUpdate

register = template.Library()


@register.simple_tag
def current_vote_percentage(polling_station):
	pu = PollUpdate.objects.order_by('-timestamp').filter(polling_station=polling_station)
	pu = pu[0]
	percentage = (pu.current_votes * 100)/polling_station.total_voters
	return percentage
