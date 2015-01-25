#This file contains some methods for dealing with Brown's 
#dining date system.

from datetime import date, datetime

def getDiningDate():
	'''Returns the current dining date as a date object. This extends until 2am the next morning.'''
	today_date = date.today()
	today_dtime = datetime.now()
	if today_dtime.hour < 2:
		return (today_date - timedelta(1))
	else:
		return today_date

def getDiningDateTime():
	''' Returns the current dining date as a datetime object. This extends until 2am the next morning. If it happens to be in the awkward 12am - 2am period, reset to 11:59 the previous day for convenience.'''
	today_dtime = datetime.now()
	if today_dtime.hour < 2:
		today_dtime = (today_dtime - timedelta(1))
		today_dtime.hour = 23
		today_dtime.minute = 59
		return today_dtime
	else:
		return today_dtime
