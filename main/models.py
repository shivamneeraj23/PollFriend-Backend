from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class LAC(models.Model):
	name = models.CharField(max_length=50, unique=True)
	unique_id = models.PositiveIntegerField(unique=True)

	def __str__(self):
		return '%s - %s' % (self.unique_id, self.name)


class PollingStation(models.Model):
	unique_id = models.CharField(max_length=10)
	lac = models.ForeignKey(LAC)
	name = models.CharField(max_length=100, unique=True)
	total_voters = models.PositiveIntegerField()
	latitude = models.DecimalField(max_digits=13,  decimal_places=10)
	longitude = models.DecimalField(max_digits=13,  decimal_places=10)

	def __str__(self):
		return '%s of LAC %s' % (self.name, self.lac)


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
		return '%s reported %s votes at %s' % (self.polling_station.name, self.current_votes, self.timestamp)


class EmergencyContact(models.Model):
	lac = models.ForeignKey(LAC)
	name = models.CharField(max_length=100)
	mobile = models.BigIntegerField(unique=True)
	# higher the level value higher is priority used to contact.
	LEVELS = (
		(0, 'Police'),
		(1, 'Sector Officer'),
		(2, 'District Election Officer'),
	)
	designation = models.SmallIntegerField(choices=LEVELS)


class POStatus(models.Model):
	presiding_officer = models.OneToOneField(PresidingOfficer)
	last_latitude = models.DecimalField(max_digits=13,  decimal_places=10)
	last_longitude = models.DecimalField(max_digits=13,  decimal_places=10)
	current_latitude = models.DecimalField(max_digits=13,  decimal_places=10)
	current_longitude = models.DecimalField(max_digits=13,  decimal_places=10)
	received_evm = models.BooleanField(default=False)
	reached_polling_station = models.BooleanField(default=False)
	sealed_evm = models.BooleanField(default=False)
	received_release = models.BooleanField(default=False)


class SOSUpdate(models.Model):
	polling_station = models.ForeignKey(PollingStation)
	message = models.TextField()
	image = models.ImageField(upload_to='/static/sosimages/')
	CONDITIONS = (
		(0, 'GOOD'),
		(1, 'BAD'),
		(2, 'DANGER'),
	)
	condition = models.SmallIntegerField(choices=CONDITIONS)