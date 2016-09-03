import requests
import json

location_names = {'Andrews': 'andrews',
				  'Jo\'s': 'littlejo',
				  'the Ratty': 'ratty',
				  'the VDub': 'vdubs',
				  'the Blue Room': 'blueroom'}

def get_count(location):
	response = json.loads(requests.get("https://i2s.brown.edu/wap/apis/localities/" + location + "/devices").content)
	return response['count']

for location in location_names:
	print("There are", get_count(location_names[location]), "people at", location + ".")