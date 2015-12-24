from flask import request, jsonify
from api import app, make_json_error, support_jsonp
from api.meta import require_client_id
import os
import requests
import json

from datetime import datetime

location_names = {'jos': 'littlejo',
                  'blueroom': 'blueroom',
                  'andrews': 'andrews',
                  'ratty': 'ratty',
                  'vdub': 'vdubs'}

'''
CIS has set up an endpoint for all WiFi requests to which we forward our
incoming requests. They protect these raw endpoints with HTTP 'BASIC'
authentication. These are our secret credentials to access their data.
'''

if 'WIFI_USERNAME' in app.config:
    wifi_username = app.config['WIFI_USERNAME']
elif 'WIFI_USERNAME' in os.environ:
    wifi_username = os.environ['WIFI_USERNAME']
else:
    print("ERROR (critical): The WiFi endpoint's username "
          "variable was not found.")

if 'WIFI_PASSWORD' in app.config:
    wifi_password = app.config['WIFI_PASSWORD']
elif 'WIFI_PASSWORD' in os.environ:
    wifi_password = os.environ['WIFI_PASSWORD']
else:
    print("ERROR (critical): The WiFi endpoint's password "
          "variable was not found.")


@app.route('/wifi')
@require_client_id()
@support_jsonp
def wifi_index():
    return make_json_error('No method specified. '
                           'See documentation for endpoints.')


@app.route('/wifi/count')
@require_client_id()
@support_jsonp
def req_wifi_count():
    ''' Endpoint for all WiFi count requests
        (see public docs for documentation) '''

    original_location = request.args.get('location', '')
    location = verify_location(original_location)

    if not location:
        return make_json_error("Invalid location: {0}".format(
            original_location))

    history = False
    history_str = request.args.get('history', '')
    if history_str in ['true', 'True']:
        history = True

    if history:
        response = requests.get("https://i2s.brown.edu/wap/apis/localities/" +
                                location + "/devices?history=true",
                                auth=(wifi_username, wifi_password))
        res_list = json.loads(response.content.decode('UTF-8'))

        history_list = []
        for res_dict in res_list:
            if not res_dict['timestamp'] or not res_dict['count']:
                return jsonify(error="WiFi data is temporarily "
                               "unavailable for this location.")

            # we'll use the user-provided location instead
            del res_dict['locality']

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
        response = requests.get("https://i2s.brown.edu/wap/apis/localities/" +
                                location + "/devices",
                                auth=(wifi_username, wifi_password))
        res_dict = json.loads(response.content.decode('UTF-8'))

        if not res_dict['timestamp'] or not res_dict['count']:
            return jsonify(error="WiFi data is temporarily "
                           "unavailable for this location.")

        # we'll use the user-provided location instead
        del res_dict['locality']

        updated_at = datetime.fromtimestamp(float(res_dict['timestamp']))
        res_dict['year'] = updated_at.year
        res_dict['month'] = updated_at.month
        res_dict['day'] = updated_at.day
        res_dict['hour'] = updated_at.hour
        res_dict['minute'] = updated_at.minute
        res_dict['second'] = updated_at.second

        return jsonify(location=original_location, **res_dict)


@app.route('/wifi/locations')
@require_client_id()
@support_jsonp
def req_wifi_locations():
    ''' Endpoint for all WiFi location requests
        (see public docs for documentation) '''

    return jsonify(locations=location_names.keys())

# Helper methods


def verify_location(location):
    ''' Return the location's keyword or None if location is invalid '''
    location = location.lower()
    if location in location_names:
        return location_names[location]
    return None
