from flask import request, jsonify
from api import app, db

from datetime import datetime, date
from difflib import get_close_matches

#TODO: Db model may need restructuring as meal names / details may change.
#		Would recommend making a primary key for each food item (some unique ID number).
#		In the current model, updating a food name would require parsing every single
#		food item, which could lead to inconsistencies. 
#
#		Suggested Change(s):
#			- Update DB model to reflect above statement
#			- change 'food' to be an array of integers.
#			- change db.dining_nutritional_info's primary key to be an int
#				- food <str> -> food <int>
#
'''
db.dining_menus contains documents of the form:
{ 'eatery': str, 
  'year': int,
  'month': int,
  'day': int,
  'start_hour': int, 		<-- these four lines describe a menu's start/end
  'start_minute': int, 			times, not the eatery's open/close times
  'end_hour': int, 
  'end_minute': int,
  'food': [ str array ]
}

db.dining_hours contains documents of the form:
{ 'eatery': str, 
  'year': int,
  'month': int,
  'day': int,
  'open_hour': int, 
  'open_minute': int, 
  'close_hour': int, 
  'close_minute': int
}

db.dining_nutritional_info contains documents of the form:
{ 'food': str,
  'ingredients': [ str array ],
  'portion_size': str,
  'calories': float,
  'fat': float,
  'saturated_fat': float,
  'cholesterol': float,
  'sodium': float,
  'carbohydrates': float,
  'fiber': float,
  'protein': float
}
'''

# simplify database names
menus = db.dining_menus
hours = db.dining_hours
nutritional_info = db.dining_nutritional_info

# TODO these should be updated with the database
# create list of valid eatery names and valid food names
valid_eatery_names = ['ratty', 'vdub', 'jos', 'ivy', 'andrews', 'blueroom']
valid_food_names = []

# TODO allow requests to omit time details and receive all menus for given day (or all open eateries, etc)

@app.route('/dining')
def dining_index():
	return jsonify(error='No method specified. See documentation for endpoints.')

@app.route('/dining/menu')
def req_dining_menu():
	''' Endpoint for all menu requests (see README for documentation) '''
	eatery = verify_eatery(request.args.get('eatery', ''))
	now = get_dining_datetime()
	year = int(request.args.get('year', now.year))
	month = int(request.args.get('month', now.month))
	day = int(request.args.get('day', -1))
	hour = int(request.args.get('hour', -1))
	minute = int(request.args.get('minute', 0))

	# if no day of month provided, set ALL time info to now
	if day < 0:
		year = now.year
		month = now.month
		day = now.day
		hour = now.hour
		minute = now.minute

	# if no hour is given, return all menus for that day
	if hour < 0:
		results = menus.find({'eatery': eatery,
							  'year': year,
							  'month': month,
							  'day': day
							 }, {'_id': 0})
		result_list = [r for r in results]
		if len(result_list) == 0:
			# no menus found for specified day
			return jsonify(error="Could not find any menus for {0}/{1}/{2}.".format(month, day, year))
		return jsonify(num_results=len(result_list), menus=result_list)

	# hour argument was supplied (or implied to be now), so find a menu for that datetime
	result = menus.find_one(
		{'eatery': eatery,
		 'year': year, 
		 'month': month, 
		 'day': day, 
		 '$or': [{'start_hour': {'$lt': hour}}, 	
		 		 {'start_hour': hour, 'start_minute': {'$lte': minute}}],
		 '$or': [{'end_hour': {'$gt': hour}}, 	
		 		 {'end_hour': hour, 'end_minute': {'$gte': minute}}]
		 }, {'_id': 0})

	if not result:
		return jsonify(error="No menu found for {0} at {1:02d}:{2:02d} {3}/{4}/{5}.".format(eatery, int(hour), int(minute), month, day, year))
	print result
	return jsonify(num_results=1, menus=[result])



@app.route('/dining/hours')
def req_dining_hours():
	''' Endpoint for all hours requests (see README for documentation) '''
	eatery = verify_eatery(request.args.get('eatery', ''))
	now = get_dining_date()
	year = int(request.args.get('year', now.year))
	month = int(request.args.get('month', now.month))
	day = int(request.args.get('day', -1))

	# if no day is provided, set ALL date info to be today
	if day < 0:
		year  = now.year
		month = now.month
		day   = now.day

	# find the hours document for this eatery on this date, exclude the ObjectID from the result
	result = hours.find_one(
		{'eatery': eatery, 
		 'year': year, 
		 'month': month, 
		 'day': day
		}, {'_id': 0})

	if not result:
		return jsonify(error="No hours found for {0} on {1}/{2}/{3}.".format(eatery, month, day, year))
	return jsonify(**result)



@app.route('/dining/find')
def req_dining_find():
	''' Endpoint for requests to find food (see README for documentation) '''
	food = verify_food(request.args.get('food', ''))

	results = menus.find({'food': {'$in': [food]}}, {'_id': 0, 'food': 0})

	result_list = [r for r in results]

	if len(result_list) == 0:
		# specified food was not found
		return jsonify(error="Could not find {0} in any of the eatery menus.".format(food))
	return jsonify(food=food, results=result_list)



@app.route('/dining/nutrition')
def req_dining_nutrition():
	''' Endpoint for nutrtitional requests (see README for documentation) '''
	food = verify_food(request.args.get('food', ''))

	result = nutritional_info.find_one({'food': food}, {'_id': 0})

	if not result:
		return jsonify(error="No nutritional information available for {0}.".format(food))
	return jsonify(**result)



@app.route('/dining/open')
def req_dining_open():
	''' Endpoint for open eatery requests (see README for documentation) '''
	now = get_dining_datetime()
	year = int(request.args.get('year', now.year))
	month = int(request.args.get('month', now.month))
	day = int(request.args.get('day', -1))
	hour = int(request.args.get('hour', -1))
	minute = int(request.args.get('minute', 0))

	# if no day of month provided, set ALL time info to now
	if day < 0:
		year = now.year
		month = now.month
		day = now.day
		hour = now.hour
		minute = now.minute

	# if no hour provided, return all open eateries on provided (or implied) date
	if hour < 0:
		results = hours.find(
			{'year': year, 
			 'month': month, 
			 'day': day, 
			 }, {'_id': 0})
		open_eateries = [r for r in results]
		if len(open_eateries) == 0:
			# no open eateries found
			return jsonify(error="No open eateries on {0}/{1}/{2}.".format(month, day, year))
		return jsonify(open_eateries=open_eateries)

	results = hours.find(
		{'year': year, 
		 'month': month, 
		 'day': day,
		 '$or': [{'open_hour': {'$lt': hour}}, 	
		 		 {'open_hour': hour, 'open_minute': {'$lte': minute}}],
		 '$or': [{'close_hour': {'$gt': hour}}, 	
		 		 {'close_hour': hour, 'close_minute': {'$gte': minute}}]
		 }, {'_id': 0})

	open_eateries = [r for r in results]

	if len(open_eateries) == 0:
		# no open eateries found
		return jsonify(error="No open eateries at {0:02d}:{1:02d} on {2}/{3}/{4}.".format(int(hour), int(minute), month, day, year))
	return jsonify(open_eateries=open_eateries)



# Helper methods

def verify_eatery(eatery):
	''' Take a string a match it to closest eatery name, or return
        None if no close matches exist
	'''
	eatery = eatery.lower()
	closest = get_close_matches(eatery, valid_eatery_names, 1)
	if len(closest) == 0:
		return None
	return closest[0]


def verify_food(food):
	''' Take a string a match it to closest food name, or return
	    None if no close matches exist
	'''
	food = food.lower()
	closest = get_close_matches(food, valid_food_names, 1)
	if len(closest) == 0:
		return food 	# TODO change this to None at some point
	return closest[0]


def get_dining_date():
	''' Return the current dining date as a date object. This extends until 2am the 
	    next morning. (e.g. 1:50AM on 11/17/2016 is reset to 11/16/2016)
	'''
	today = date.today()
	now = datetime.now()
	if now.hour < 2:
		return (today - timedelta(1))
	else:
		return today


def get_dining_datetime():
	''' Return the current dining date as a datetime object. This extends until 2am 
	    the next morning. If it happens to be in the awkward 12am - 2am period, reset 
	    to 11:59 the previous day for convenience.
	'''
	now = datetime.now()
	if now.hour < 2:
		now = (now - timedelta(1))
		now.hour = 23
		now.minute = 59
		return now
	else:
		return now

