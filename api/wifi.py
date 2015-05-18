from flask import request, jsonify
from api import app, db, make_json_error, limiter, RATE_LIMIT, support_jsonp
from meta import is_valid_client, log_client, INVALID_CLIENT_MSG
import requests
import json

from datetime import datetime, date, timedelta

location_names = {'jos': 'littlejo', 
				  'blueroom': 'blueroom',
				  'andrews': 'andrews',
				  'ratty': 'ratty',
				  'vdub': 'vdubs'}


@app.route('/wifi')
@limiter.shared_limit(RATE_LIMIT, 'wifi')
@support_jsonp
def wifi_index():
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/wifi', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)
	return make_json_error('No method specified. See documentation for endpoints.')



@app.route('/wifi/count')
@limiter.shared_limit(RATE_LIMIT, 'wifi')
@support_jsonp
def req_wifi_count():
	''' Endpoint for all WiFi count requests (see public docs for documentation) '''

	# TODO enable wifi API again
	return jsonify(error="We have been asked to disable this API until further notice. Check our home page for updates.")


	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/wifi/count', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

	original_location = request.args.get('location', '')
	location = verify_location(original_location)

	if not location:
		return make_json_error("Invalid location: {0}".format(location))

	history = False
	history_str = request.args.get('history', '')
	if history_str in ['true', 'True']:
		history = True

	if history:
		response = requests.get("https://i2s.brown.edu/wap/apis/localities/" + location + "/devices?history=true")
		res_list = json.loads(response.content)
		history_list = []
		for res_dict in res_list:
			del res_dict['locality']	# we'll use the user-provided location instead

			updated_at = datetime.fromtimestamp(float(res_dict['timestamp']))
			res_dict['year'] = updated_at.year
			res_dict['month'] = updated_at.month
			res_dict['day'] = updated_at.day
			res_dict['hour'] = updated_at.hour
			res_dict['minute'] = updated_at.minute
			res_dict['second'] = updated_at.second
			history_list += [res_dict]

		return jsonify(location=original_location, history=history_list)
	else:
		response = requests.get("https://i2s.brown.edu/wap/apis/localities/" + location + "/devices")
		res_dict = json.loads(response.content)
		del res_dict['locality']	# we'll use the user-provided location instead

		updated_at = datetime.fromtimestamp(float(res_dict['timestamp']))
		res_dict['year'] = updated_at.year
		res_dict['month'] = updated_at.month
		res_dict['day'] = updated_at.day
		res_dict['hour'] = updated_at.hour
		res_dict['minute'] = updated_at.minute
		res_dict['second'] = updated_at.second

		return jsonify(location=original_location, **res_dict)



@app.route('/wifi/locations')
@limiter.shared_limit(RATE_LIMIT, 'wifi')
@support_jsonp
def req_wifi_locations():
	''' Endpoint for all WiFi location requests (see public docs for documentation) '''
	
	# TODO enable wifi API again
	return jsonify(error="We have been asked to disable this API until further notice. Check our home page for updates.")


	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/wifi/locations', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

	return jsonify(locations=location_names.keys())

# Helper methods

def verify_location(location):
	''' Return the location's keyword or None if location is invalid '''
	location = location.lower()
	if location in location_names:
		return location_names[location]
	return None