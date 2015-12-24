from flask import render_template, url_for, request, redirect
from functools import wraps
from api import make_json_error
from api import app, db
from api.scripts.add_client import add_client_id
from api.scripts.email_handler import send_id_email
from api.scripts.stats import get_total_requests
from datetime import datetime

'''
DATABASE OBJECTS: View templates on the private, repository README.
'''

# simplify collection names
clients = db.clients

# Messages for success/failure during Client ID signup
SUCCESS_MSG = "Your Client ID has been emailed to you!"
FAILURE_MSG = ("Your request could not be processed. "
               "Please email 'joseph_engelman@brown.edu' for "
               "manual registration.")


@app.route('/')
def root():
    signed_up = request.args.get('signedup', '')
    num_requests = get_total_requests()
    if signed_up == 'true':
        return render_template('documentation.html',
                               message=SUCCESS_MSG,
                               num_requests=num_requests)
    if signed_up == 'false':
        return render_template('documentation.html',
                               message=FAILURE_MSG,
                               num_requests=num_requests)
    else:
        return render_template('documentation.html', num_requests=num_requests)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        firstname = request.form['firstname'].strip()
        lastname = request.form['lastname'].strip()
        email = request.form['email'].strip()
        client_id = add_client_id(email, firstname + " " + lastname)
        if client_id:
            send_id_email(email, firstname, client_id)
            return redirect(url_for('root', signedup='true'))
        else:
            return redirect(url_for('root', signedup='false'))


# Static responses

INVALID_CLIENT_MSG = "invalid client id"


# Helper methods

def is_valid_client(client_id):
    ''' Return True if client ID is valid, False otherwise '''
    if client_id == 'missing_client':
        # requests without a client_id should default to 'missing_client'
        return False

    client = clients.find_one({'client_id': client_id})
    if client and 'valid' in client and client['valid']:
        # client exists in database and is marked as valid
        return True
    print("Client ID", client_id, "not found in client collection")
    return False


def log_client(client_id, endpoint, timestamp):
    ''' Log a client's activity with the time of occurence
        Return True if successfully logged, otherwise False
    '''
    result = clients.update(
        {'client_id': client_id},
        {
            '$inc': {'requests': 1},
            '$push': {
                'activity': {
                    'endpoint': endpoint,
                    'timestamp': timestamp
                }
            }
        })
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    print("Bad result from log_client: ", result)
    return False


def invalidate_client(client_id):
    ''' Invalidate a client, revoking future access
        Return True if client's access mode was modified to False, or
            return False if client's access mode was already False or
            the operation was unsuccessful
    '''
    result = clients.update({'client_id': client_id},
                            {'$set': {'valid': False}})
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    return False


def validate_client(client_id):
    ''' Validate a client, enabling future access
        Return True if client's access mode was modified to True, or
            return False if client's access mode was already True or
            the operation was unsuccessful
    '''
    result = clients.update({'client_id': client_id},
                            {'$set': {'valid': True}})
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    return False


class require_client_id(object):
    ''' Wraps view functions to require valid client IDs.
        Must be included *after* the app.route decorator.
        Optionally takes a custom endpoint string to log on success.'''
    def __init__(self, endpoint=None):
        self.endpoint = endpoint

    def __call__(self, f):
        @wraps(f)
        def wrapper_fn(*args, **kwargs):
            ep = self.endpoint
            if ep is None:
                ep = str(request.url_rule)

            client_id = request.args.get('client_id', 'missing_client')
            if is_valid_client(client_id):
                log_client(client_id, ep, str(datetime.now()))
                return f(*args, **kwargs)
            else:
                return make_json_error(INVALID_CLIENT_MSG)

        return wrapper_fn
