from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class PollingStation(models.Model):
	id = models.CharField(max_length=10, primary_key=True)
	name = models.CharField(max_length=250, unique=True)
	total_voters = models.PositiveIntegerField()
	latitude = models.DecimalField(max_digits=13,  decimal_places=10)
	longitude = models.DecimalField(max_digits=13,  decimal_places=10)

	def __str__(self):
		return self.name


class PresidingOfficer(models.Model):
	# username can be used as presiding officers unique id format " 9/001 to 15/198 "
	user = models.OneToOneField(User)

	def _get_full_name(self):
		return '%s %s' % (self.user.first_name, self.user.last_name)

	full_name = property(_get_full_name)
	polling_station = models.OneToOneField(PollingStation)
	mobile = models.BigIntegerField(unique=True)

	def __str__(self):
		return self.full_name


class PollUpdate(models.Model):
	polling_station = models.ForeignKey(PollingStation)
	current_votes = models.PositiveIntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '%s reported %d votes at %s' % (self.polling_station.name, self.current_votes, self.timestamp)

