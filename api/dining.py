from flask import request, jsonify
from api import app, db, make_json_error, limiter, RATE_LIMIT, support_jsonp
from meta import is_valid_client, log_client, INVALID_CLIENT_MSG

from datetime import datetime, date, timedelta
from difflib import get_close_matches

'''
DATABASE OBJECTS: View templates on the private, repository README.
Nutritional info is not yet finished. Contact Joe for a preliminary template. 
'''

# simplify database names
menus = db.dining_menus
hours = db.dining_hours
nutritional_info = db.dining_nutritional_info
all_foods = db.dining_all_foods

# TODO these should be updated with the database
# create list of valid eatery names and valid food names
valid_eatery_names = ['ratty', 'vdub', 'jos', 'ivy', 'andrews', 'blueroom']
valid_food_names = []


@app.route('/dining')
@limiter.shared_limit(RATE_LIMIT, 'dining')
@support_jsonp
def dining_index():
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/dining', str(datetime.now()))
		return make_json_error('No method specified. See documentation for endpoints.')
	return make_json_error(INVALID_CLIENT_MSG)



@app.route('/dining/menu')
@limiter.shared_limit(RATE_LIMIT, 'dining')
@support_jsonp
def req_dining_menu():
	''' Endpoint for all menu requests (see README for documentation) '''
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/dining/menu', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

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
							 }, {'_id': 0, 'food': 0})
		result_list = [r for r in results]
		if len(result_list) == 0:
			# no menus found for specified day
			return make_json_error("Could not find any menus for {0}/{1}/{2}.".format(month, day, year))
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
		 }, {'_id': 0, 'food': 0})

	if not result:
		return make_json_error("No menu found for {0} at {1:02d}:{2:02d} {3}/{4}/{5}.".format(eatery, int(hour), int(minute), month, day, year))
	return jsonify(num_results=1, menus=[result])



@app.route('/dining/hours')
@limiter.shared_limit(RATE_LIMIT, 'dining')
@support_jsonp
def req_dining_hours():
	''' Endpoint for all hours requests (see README for documentation) '''
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/dining/hours', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

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

	# find the hours document(s) for this eatery on this date, exclude the ObjectID from the result
	# NOTE: some eateries open/close multiple times a day -> thus, multiple hours documents per day
	results = hours.find(
		{'eatery': eatery, 
		 'year': year, 
		 'month': month, 
		 'day': day
		}, {'_id': 0})

	result_list = [r for r in results]

	if len(result_list) == 0:
		return make_json_error("No hours found for {0} on {1}/{2}/{3}.".format(eatery, month, day, year))
	return jsonify(num_results=len(result_list), results=result_list)



@app.route('/dining/find')
@limiter.shared_limit(RATE_LIMIT, 'dining')
@support_jsonp
def req_dining_find():
	''' Endpoint for requests to find food (see README for documentation) '''
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/dining/find', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

	food = verify_food(request.args.get('food', ''))

	results = menus.find({'food': {'$in': [food]}}, {'_id': 0, 'food': 0})

	result_list = [r for r in results]

	if len(result_list) == 0:
		# specified food was not found
		return make_json_error("Could not find {0} in any of the eatery menus.".format(food))
	return jsonify(food=food, results=result_list, num_results=len(result_list))



@app.route('/dining/nutrition')
@limiter.shared_limit(RATE_LIMIT, 'dining')
@support_jsonp
def req_dining_nutrition():
	''' Endpoint for nutrtitional requests (see README for documentation) '''
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/dining/nutrition', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

	food = verify_food(request.args.get('food', ''))

	result = nutritional_info.find_one({'food': food}, {'_id': 0})

	if not result:
		return make_json_error("No nutritional information available for {0}.".format(food))
	return jsonify(**result)



@app.route('/dining/open')
@limiter.shared_limit(RATE_LIMIT, 'dining')
@support_jsonp
def req_dining_open():
	''' Endpoint for open eatery requests (see README for documentation) '''
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/dining/open', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

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
			return make_json_error("No open eateries on {0}/{1}/{2}.".format(month, day, year))
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
		return make_json_error("No open eateries at {0:02d}:{1:02d} on {2}/{3}/{4}.".format(int(hour), int(minute), month, day, year))
	return jsonify(open_eateries=open_eateries)

@app.route('/dining/all_food')
@limiter.shared_limit(RATE_LIMIT, 'dining')
@support_jsonp
def req_dining_all_food():
	''' Endpoint for all food requests (see README for documentation) '''
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/dining/all_food', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

	eatery = verify_eatery(request.args.get('eatery', ''))

	if not eatery:
		return make_json_error("No eatery name provided or invalid eatery name.")

	result = all_foods.find_one({'eatery': eatery}, {'_id': 0})

	if not result:
		return make_json_error("No food information available for {0}.".format(eatery))
	return jsonify(**result)


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
		now.replace(hour=23, minute=59)
		return now
	else:
		return now

