from flask import request, jsonify
from api import app, db

from datetime import datetime
import json

'''
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

hours = db.dining_hours
nutritional_info = db.dining_nutritional_info

# TODO verify all incoming values for eateries, dates, etc

@app.route('/dining/menu')
def req_dining_menu():
	eatery = request.args.get('eatery')
	now = datetime.now()	# use current datetime as default
	year = request.args.get('year', now.year)
	month = request.args.get('month', now.month)
	day = request.args.get('day', now.day)
	hour = request.args.get('hour', now.hour)
	minute = request.args.get('minute', now.minute)

	# TODO find menu for eatery at given time

@app.route('/dining/hours')
def req_dining_hours():
	eatery = request.args.get('eatery')
	now = datetime.now()	# use current date as default
	year = request.args.get('year', now.year)
	month = request.args.get('month', now.month)
	day = request.args.get('day', now.day)

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
	food = request.args.get('food', None)

	# TODO finding eatery serving food

@app.route('/dining/nutrition')
def req_dining_nutrition():
	food = request.args.get('food', None)

	# TODO do any preprocessing on 'food' string (lowercasing, stemming, etc)

	result = nutritional_info.find_one({'food': food}, {'_id': 0})

	if not result:
		return jsonify(error="No nutritional information available for {0}.".format(food))
	return jsonify(**result)

@app.route('/dining/open')
def req_dining_open():
	now = datetime.now()	# use current datetime as default
	year = request.args.get('year', now.year)
	month = request.args.get('month', now.month)
	day = request.args.get('day', now.day)
	hour = request.args.get('hour', now.hour)
	minute = request.args.get('minute', now.minute)

	results = hours.find(
		{'year': year, 
		 'month': month, 
		 'day': day, 
		 'open_hour': {'$lte': hour}, 
		 'open_minute': {'$lte': minute},
		 'close_hour': {'$gte': hour},
		 'close_minute': {'$gte': minute}
		 }, {'_id': 0})

	open_eateries = [r for r in results]

	if len(open_eateries) == 0:
		# no open eateries found
		return jsonify(error="No open eateries at {0:02d}:{1:02d} on {2}/{3}/{4}.".format(int(hour), int(minute), month, day, year))
	return jsonify(open_eateries=open_eateries)





