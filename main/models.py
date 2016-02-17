from django.db import models
from django.template.defaultfilters import slugify
# Create your models here.


class PollingBooth(models.Model):
	region_name = models.CharField(max_length=250, unique=True)
	number = models.CharField(max_length=10, unique=True)
	latitude = models.DecimalField(max_digits=3,  decimal_places=10)
	longitude = models.DecimalField(max_digits=3,  decimal_places=10)

	def __str__(self):
		return self.region_name

