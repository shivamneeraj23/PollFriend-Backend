from django.db import models
from django.contrib.auth.models import User
# from djnago.template.defaultfilters import slugify
# Create your models here.

USER_TYPE_CHOICES = (
	(1, 'Presiding Officer'),
	(2, 'Sector Officer'),
	(3, 'Admin Manual'),
	(4, 'Admin Bot'),
)


class LAC(models.Model):
	name = models.CharField(max_length=50, unique=True)
	unique_id = models.PositiveIntegerField(unique=True)
	constituent_magistrate = models.CharField(max_length=100)
	constituent_magistrate_mobile = models.BigIntegerField()

	def __str__(self):
		return '%s - %s' % (self.unique_id, self.name)


class SectorOffice(models.Model):
	name = models.CharField(max_length=50, null=True, blank=True)
	lac = models.ForeignKey(LAC)
	sector_officer = models.CharField(max_length=100)
	sector_officer_mobile = models.BigIntegerField()
	username = models.CharField(max_length=50, null=True, blank=True, unique=True)
	password = models.CharField(max_length=50, null=True, blank=True)
	api_key = models.CharField(max_length=70, null=True, blank=True)

	def __str__(self):
		return '%s' % self.sector_officer


class PollingStation(models.Model):
	unique_id = models.CharField(max_length=10)
	sector_office = models.ForeignKey(SectorOffice)
	name = models.CharField(max_length=100, unique=False)
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
		return '%s - %s' % (self.unique_id, self.name)


class PresidingOfficer(models.Model):
	# username can be used as presiding officers unique id format " 9/001 to 15/198 "
	username = models.CharField(max_length=50, null=True, blank=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50, null=True, blank=True)

	def _get_full_name(self):
		return '%s %s' % (self.first_name, self.last_name)

	full_name = property(_get_full_name)
	polling_station = models.OneToOneField(PollingStation)
	mobile = models.BigIntegerField(null=True, blank=True)
	second_mobile = models.BigIntegerField(null=True, blank=True)
	api_key = models.CharField(max_length=70, null=True, blank=True)
	device_key = models.CharField(max_length=300, null=True, blank=True)
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
	time_field = models.SmallIntegerField(null=True, blank=True)
	updated_by = models.SmallIntegerField(choices=USER_TYPE_CHOICES, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '%s reported %s votes at %s' % (self.polling_station, self.current_votes, self.time_field)


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
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True)
	solved = models.BooleanField(default=False)


class EVM(models.Model):
	polling_station = models.ForeignKey(PollingStation)
	unique_id = models.CharField(max_length=50)


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
	device_key = models.CharField(max_length=300, unique=False, null=True, blank=True)
	timestamp = models.DateTimeField(auto_now=True)


class Message(models.Model):
	user = models.ForeignKey(User)
	count_id = models.IntegerField()
	message = models.TextField()
	presiding_officer = models.ForeignKey(PresidingOfficer)
	timestamp = models.DateTimeField(auto_now=True)


class OtherDetails(models.Model):
	faq = models.TextField()
	guidelines = models.TextField()
	timestamp = models.DateTimeField(auto_now=True)
