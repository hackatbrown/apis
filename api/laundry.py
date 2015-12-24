# vim: set ts=4 sts=4 sw=4 expandtab:
from flask import request, jsonify
from api import app, db, make_json_error, support_jsonp
from api.meta import is_valid_client, log_client, INVALID_CLIENT_MSG
from functools import wraps

from datetime import datetime  # , date, timedelta
# from difflib import get_close_matches

'''
DATABASE OBJECTS: View templates on the private, repository README.
Nutritional info is not yet finished. Contact Joe for a preliminary template.
'''

# simplify database names
ldb = db.laundry


class requireKey(object):
    def __init__(self, endpoint_name):
        self.endpoint_name = endpoint_name

    def __call__(self, f):
        @wraps(f)
        def wrapped_fn(*args, **kwargs):
            client_id = request.args.get('client_id', 'missing_client')
            if is_valid_client(client_id):
                log_client(client_id, '/dining', str(datetime.now()))
                return f(*args, **kwargs)
            else:
                return make_json_error(INVALID_CLIENT_MSG)
        return wrapped_fn


@app.route('/laundry')
@support_jsonp
@requireKey('/laundry')
def laundry_index():
    return make_json_error('No method specified. '
                           'See documentation for endpoints.')


@app.route('/laundry/rooms')
@support_jsonp
@requireKey('/laundry/rooms')
def req_laundry_room_list():
    results = ldb.find({}, {'_id': False, 'machines': False})
    result_list = [r for r in results]
    return jsonify(num_result=len(result_list), results=result_list)


@app.route('/laundry/rooms/<room_id>')
@support_jsonp
@requireKey('/laundry/rooms/<room_id>')
def req_room_detail(room_id):
    room = ldb.find_one({'id': str(room_id)}, {'_id': False})
    if room is None:
        return make_json_error('Room not found')
    return jsonify(result=room)


@app.route('/laundry/rooms/<room_id>/machines')
@support_jsonp
@requireKey('/laundry/rooms/<room_id>/machines')
def req_machines(room_id):
    # TODO support a getStatus parameter to optionally get machine statuses
    get_statuses = request.args.get('get_statuses')
    print(get_statuses)

    # TODO make a type field to filter on (washer, dryer, etc)

    room = ldb.find_one({'id': str(room_id)}, {'_id': False, 'machines': True})
    if room is None:
        return make_json_error('Room not found')
    return jsonify(results=room['machines'])


@app.route('/laundry/rooms/<room_id>/machines/<machine_id>')
@support_jsonp
@requireKey('/laundry/rooms/<room_id>/machines/<machine_id>')
def req_machine_details(room_id, machine_id):
    # TODO support a getStatus parameter to optionally get machine statuses
    get_statuses = request.args.get('get_statuses')
    print(get_statuses)

    m = ldb.find_one({'id': str(room_id), 'machines.id': str(machine_id)},
                     {'_id': False, 'machines': True})
    if m is None:
        return make_json_error("Machine or room not found")

    m = list(filter(lambda x: x['id'] == str(machine_id), m['machines']))
    if len(m) == 0:
        return make_json_error("Machine not found")

    return jsonify(result=m[0])
