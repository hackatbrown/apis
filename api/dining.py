from flask import request, jsonify
from api import app, db

from datetime import datetime
import json

'''
db.dining_hours contains entries of the form:
{ 'eatery': str, 
  'year': int,
  'month': int,
  'day': int,
  'open_hour': int, 
  'open_minute': int, 
  'close_hour': int, 
  'close_minute': int
}

'''

hours = db.dining_hours

@app.route('/dining/menu')
def req_dining_menu():
	eatery_name = request.args.get('eatery')
	now = datetime.now()	# use current datetime as default
	year = request.args.get('year', now.year)
	month = request.args.get('month', now.month)
	day = request.args.get('day', now.day)
	hour = request.args.get('hour', now.hour)
	minute = request.args.get('minute', now.minute)

	# TODO find menu for eatery at given time

@app.route('/dining/hours')
def req_dining_hours():
	eatery= request.args.get('eatery')
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
		# TODO write a better error response
		return jsonify(error="No hours found for the eatery on specified date.")
	return jsonify(**result)

@app.route('/dining/find')
def req_dining_find():
	food = request.args.get('food', None)

	# TODO finding eatery serving food

@app.route('/dining/nutrition')
def req_dining_nutrition():
	food = request.args.get('food', None)

	# TODO find nutritional info for food

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
		# TODO write a better error response
		return jsonify(error="No open eateries at specified time.")
	return jsonify(open_eateries=open_eateries)





