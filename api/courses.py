from flask import request, jsonify
from api import app, db, make_json_error, limiter, RATE_LIMIT, support_jsonp
from meta import is_valid_client, log_client, INVALID_CLIENT_MSG

from datetime import datetime, date, timedelta



@app.route('/courses')
@limiter.shared_limit(RATE_LIMIT, 'courses')
@support_jsonp
def courses_index():
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/courses', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)
	return make_json_error('No method specified. See documentation for endpoints.')



@app.route('/courses/find')
@limiter.shared_limit(RATE_LIMIT, 'courses')
@support_jsonp
def req_courses_count():
	''' Endpoint for all courses find requests (see public docs for documentation) '''
	client_id = request.args.get('client_id', 'missing_client')
	if is_valid_client(client_id):
		log_client(client_id, '/wifi/count', str(datetime.now()))
	else:
		return make_json_error(INVALID_CLIENT_MSG)

	course_id = request.args.get('id', '')

	if len(course_id) == 0:
		return jsonify(error="No course ID provided.")

	# TODO find course information for the given ID and return it
	example_course = {'department_code': 'CSCI',
					  'department_name': 'Computer Science',
					  'course_number:': 0170,
					  'professor': 'Amy Greenwald'}
	course = example_course

	# The double asterisks automatically unpack the course dictionary
	# (e.g. "**course:" => "department_code='CSCI', department_name='Computer Science', etc")
	return jsonify(**course)




# Helper methods

# TODO add any helper methods (methods that might be useful for multiple endpoints) here
