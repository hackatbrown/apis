from flask import request
from api import app

from datetime import datetime
import json

@app.route('/dining/menu')
def req_dining_menu():
	eatery = request.args.get('eatery')
	now = datetime.now()	# use current datetime as default
	year = request.args.get('year', now.year)
	month = request.args.get('month', now.month)
	day = request.args.get('day', now.day)
	hour = request.args.get('hour', now.hour)
	minute = request.args.get('minute', now.minute)

	#TODO find menu for eatery at given time

@app.route('/dining/hours')
def req_dining_hours():
	eatery = request.args.get('eatery')
	now = datetime.now()	# use current date as default
	year = request.args.get('year', now.year)
	month = request.args.get('month', now.month)
	day = request.args.get('month', now.day)

	# TODO find hours for eatery on date

@app.route('/dining/find')
def req_dining_find():
	food = request.args.get('food', None)

	# TODO finding eatery serving food

@app.route('/dining/nutrition')
def req_dining_nutrition():
	food = request.args.get('food', None)

	# TODO find nutritional info for food

@app.route('/dining/open_eateries')
def req_dining_open_eateries():
	now = datetime.now()	# use current datetime as default
	year = request.args.get('year', now.year)
	month = request.args.get('month', now.month)
	day = request.args.get('day', now.day)
	hour = request.args.get('hour', now.hour)
	minute = request.args.get('minute', now.minute)

	# TODO find open eateries


