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
		return make_json_error('No method specified. See documentation for endpoints.')
	return make_json_error(INVALID_CLIENT_MSG)



@app.route('/wifi/count')
@limiter.shared_limit(RATE_LIMIT, 'wifi')
@support_jsonp
def req_wifi_count():
	''' Endpoint for all WiFi count requests (see README for documentation) '''
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/wifi/count', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

	original_location = request.args.get('location', '')
	location = verify_location(original_location)

	if not location:
		return make_json_error("Invalid location: {0}".format(location))

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



# Helper methods

def verify_location(location):
	''' Return the location's keyword or None if location is invalid '''
	location = location.lower()
	if location in location_names:
		return location_names[location]
	return None
