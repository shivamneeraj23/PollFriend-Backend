import math


def degToRad(deg):
	return deg*(math.pi/180.00)


def getDistBetweenTwoPoints(lat1, long1, lat2, long2):
	lat1 = float(lat1)
	lat2 = float(lat2)
	long1 = float(long1)
	long2 = float(long2)
	R = 6371000 # Radius of Earth in meter
	dLat = degToRad(lat2-lat1) # degree to radian conversion
	dLong = degToRad(long2-long1)
	a = ((math.sin(dLat/2))**2) + ((math.sin(dLong/2))**2) * (math.cos(degToRad(lat1)) * math.cos(degToRad(lat2)))
	b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	c = R * b # distance in meter
	return c

