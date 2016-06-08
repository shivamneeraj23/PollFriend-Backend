"""Haversine Formula
This formula calculates distance between two points (using pair of lat, long) on the surface of Earth.
"""
import math
__author__ = "Wicklers"


def degToRad(deg):
	"""Converts degree (unit) to radian (unit)
	:param deg: Degree (float) to convert to Radian.
	:return: Radian (float)
	"""
	return deg*(math.pi/180.00)  # conversion


def getDistBetweenTwoPoints(lat1, long1, lat2, long2):
	"""Gives distance between two points in meter(s).
	Two points should be in latitude, longitude format.
	:param lat1: Latitude of first point (float or Decimal), in degree
	:param long1: Longitude of first point (float or Decimal), in degree
	:param lat2: Latitude of second point (float or Decimal), in degree
	:param long2: Longitude of second point (float or Decimal), in degree
	:return: Distance in meter (float)
	"""
	# if lat, long are in Decimal data type, we first change them to float type
	lat1, lat2, long1, long2 = float(lat1), float(lat2), float(long1), float(long2)
	R = 6371000  # radius of Earth in meter

	dLat = degToRad(lat2-lat1)  # degree to radian conversion
	dLong = degToRad(long2-long1)

	a = ((math.sin(dLat/2))**2) + ((math.sin(dLong/2))**2) * (math.cos(degToRad(lat1)) * math.cos(degToRad(lat2)))
	b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	c = R * b  # distance in meter
	return c
