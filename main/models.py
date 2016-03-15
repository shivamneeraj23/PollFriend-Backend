from django.db import models
from django.contrib.auth.models import User
# from djnago.template.defaultfilters import slugify
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
	total_voters = models.PositiveIntegerField(blank=True, null=True)
	latitude = models.DecimalField(max_digits=13,  decimal_places=10)
	longitude = models.DecimalField(max_digits=13,  decimal_places=10)
	CONDITIONS = (
		(1, 'GOOD'),
		(2, 'OK'),
		(3, 'BAD'),
	)
	condition = models.SmallIntegerField(choices=CONDITIONS, null=True, blank=True)

	def __str__(self):
		return '%s of LAC %s' % (self.name, self.lac)


class PresidingOfficer(models.Model):
	# username can be used as presiding officers unique id format " 9/001 to 15/198 "
	username = models.CharField(max_length=50, unique=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)

	def _get_full_name(self):
		return '%s %s' % (self.first_name, self.last_name)

	full_name = property(_get_full_name)
	polling_station = models.OneToOneField(PollingStation)
	mobile = models.BigIntegerField(unique=True)
	api_key = models.CharField(max_length=70, null=True, blank=True)
	device_key = models.CharField(max_length=300, unique=True, null=True, blank=True)
	last_login = models.DateTimeField(blank=True, null=True)
	last_logout = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return self.full_name

	def save(self, *args, **kwargs):
		super(PresidingOfficer, self).save(*args, **kwargs)
		try:
			po_status = POStatus.objects.get(presiding_officer=self)
			po_status.save()
		except POStatus.DoesNotExist:
			po_status = POStatus()
			po_status.presiding_officer = self
			po_status.save()


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
		(1, 'Police'),
		(2, 'Sector Officer'),
		(3, 'District Election Officer'),
	)
	designation = models.SmallIntegerField(choices=LEVELS)


class POStatus(models.Model):
	presiding_officer = models.OneToOneField(PresidingOfficer)
	received_evm = models.BooleanField(default=False)
	received_evm_timestamp = models.DateTimeField(blank=True, null=True)
	reached_polling_station = models.BooleanField(default=False)
	reached_polling_station_timestamp = models.DateTimeField(blank=True, null=True)
	mock_poll_starts = models.BooleanField(default=False)
	mock_poll_starts_timestamp = models.DateTimeField(blank=True, null=True)
	mock_poll_ends = models.BooleanField(default=False)
	mock_poll_ends_timestamp = models.DateTimeField(blank=True, null=True)
	mock_poll_resetted = models.BooleanField(default=False)
	mock_poll_resetted_timestamp = models.DateTimeField(blank=True, null=True)
	poll_starts = models.BooleanField(default=False)
	poll_starts_timestamp = models.DateTimeField(blank=True, null=True)
	poll_ends = models.BooleanField(default=False)
	poll_ends_timestamp = models.DateTimeField(blank=True, null=True)
	sealed_evm = models.BooleanField(default=False)
	sealed_evm_timestamp = models.DateTimeField(blank=True, null=True)
	received_release = models.BooleanField(default=False)
	received_release_timestamp = models.DateTimeField(blank=True, null=True)
	reached_dc = models.BooleanField(default=False)
	reached_dc_timestamp = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return self.presiding_officer.full_name


class SOSUpdate(models.Model):
	polling_station = models.ForeignKey(PollingStation)
	message = models.TextField(null=True, blank=True)
	image = models.ImageField(upload_to='sosimages/', null=True, blank=True)
	CONDITIONS = (
		(1, 'BAD'),
		(2, 'DANGER'),
	)
	condition = models.SmallIntegerField(choices=CONDITIONS, null=True, blank=True)
	SUBJECTS = (
		(1, 'EVM'),
		(2, 'POLLING STATION'),
		(3, 'OTHER'),
	)
	subject = models.SmallIntegerField(choices=SUBJECTS, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now=True, null=True, blank=True)


class EVM(models.Model):
	polling_station = models.ForeignKey(PollingStation)
	unique_id = models.CharField(max_length=50, unique=True)


class POLocation(models.Model):
	presiding_officer = models.ForeignKey(PresidingOfficer)
	latitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True)
	longitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, null=True)
	timestamp = models.DateTimeField(auto_now=True)


class PSImage(models.Model):
	polling_station = models.ForeignKey(PollingStation)
	image = models.ImageField(upload_to='psimages/', null=True, blank=True)
	timestamp = models.DateTimeField(auto_now=True)


class WebDevice(models.Model):
	user = models.OneToOneField(User)
	device_key = models.CharField(max_length=300, unique=True, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now=True)


class Message(models.Model):
	user = models.ForeignKey(User)
	count_id = models.IntegerField()
	message = models.TextField()
	presiding_officer = models.ForeignKey(PresidingOfficer)
	timestamp = models.DateTimeField(auto_now=True)