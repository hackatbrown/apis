from flask import request, jsonify
from api import app, db

from datetime import datetime
from difflib import get_close_matches

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

# TODO consider the case where eateries are open past midnight ($lt, $gt operators may produce incorrect results)
# TODO allow requests to omit time details and receive all menus for given day (or all open eateries, etc)

@app.route('/dining')
def dining_index():
	return jsonify(error='No method specified.')

@app.route('/dining/menu')
def req_dining_menu():
	eatery = verify_eatery(request.args.get('eatery', ''))
	now = datetime.now()	# use current datetime as default
	year = int(request.args.get('year', now.year))
	month = int(request.args.get('month', now.month))
	day = int(request.args.get('day', now.day))
	hour = int(request.args.get('hour', now.hour))
	minute = int(request.args.get('minute', now.minute))

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
	return jsonify(**result)



@app.route('/dining/hours')
def req_dining_hours():
	eatery = verify_eatery(request.args.get('eatery', ''))
	now = datetime.now()	# use current date as default
	year = int(request.args.get('year', now.year))
	month = int(request.args.get('month', now.month))
	day = int(request.args.get('day', now.day))

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
	food = verify_food(request.args.get('food', ''))

	results = menus.find({'food': {'$in': [food]}}, {'_id': 0, 'food': 0})

	result_list = [r for r in results]

	if len(result_list) == 0:
		# specified food was not found
		return jsonify(error="Could not find {0} in any of the eatery menus.".format(food))
	return jsonify(food=food, results=result_list)



@app.route('/dining/nutrition')
def req_dining_nutrition():
	food = verify_food(request.args.get('food', ''))

	result = nutritional_info.find_one({'food': food}, {'_id': 0})

	if not result:
		return jsonify(error="No nutritional information available for {0}.".format(food))
	return jsonify(**result)



@app.route('/dining/open')
def req_dining_open():
	now = datetime.now()	# use current datetime as default
	year = int(request.args.get('year', now.year))
	month = int(request.args.get('month', now.month))
	day = int(request.args.get('day', now.day))
	hour = int(request.args.get('hour', now.hour))
	minute = int(request.args.get('minute', now.minute))

	results = hours.find(
		{'year': year, 
		 'month': month, 
		 'day': day, 
		 'open_hour': {'$lte': hour}, 			# TODO fix this logic like in dining/menu
		 'open_minute': {'$lte': minute},
		 'close_hour': {'$gte': hour},
		 'close_minute': {'$gte': minute}
		 }, {'_id': 0})

	open_eateries = [r for r in results]

	if len(open_eateries) == 0:
		# no open eateries found
		return jsonify(error="No open eateries at {0:02d}:{1:02d} on {2}/{3}/{4}.".format(int(hour), int(minute), month, day, year))
	return jsonify(open_eateries=open_eateries)



# helper methods

# verify_eatery - takes a string and matches to closest eatery name, 
#  					or returns None if no close matches exist
def verify_eatery(eatery):
	eatery = eatery.lower()
	closest = get_close_matches(eatery, valid_eatery_names, 1)
	if len(closest) == 0:
		return None
	return closest[0]

# verify_food - takes a string and matches to closest food name,
#				  or returns None if no close matches exist
def verify_food(food):
	food = food.lower()
	closest = get_close_matches(food, valid_food_names, 1)
	if len(closest) == 0:
		return food 	# change this to None at some point
	return closest[0]

