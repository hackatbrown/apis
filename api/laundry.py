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
def req_laundry_rooms():
    results = ldb.find({}, {'_id': 0})
    result_list = [r for r in results]
    return jsonify(num_result=len(result_list), results=result_list)
