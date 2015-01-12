#This file contains some methods for dealing with Brown's 
#dining date system.

from datetime import date

def getDiningDate():
	'''Returns the current dining date as a date object. This extends until 2am the next morning.'''
	today_date = date.today()
	today_dtime = datetime.today()
	#if it's before 2am, paxson doesn't consider it a new dining day yet
	if (today_dtime.hour < 2):
		return (today_date - timedelta(1))
	else:
		return today_date




