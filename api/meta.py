from flask import jsonify, render_template, url_for, request, redirect
from api import app, db
from api.scripts.add_client import add_client_id
from api.scripts.email_handler import send_id_email
from api.scripts.stats import get_total_requests

'''
DATABASE OBJECTS: View templates on the private, repository README.
'''

# simplify collection names
clients = db.clients

# Messages for success/failure during Client ID signup
SUCCESS_MSG = "Your Client ID has been emailed to you!"
FAILURE_MSG = "Your request could not be processed. Please email 'joseph_engelman@brown.edu' for manual registration."


@app.route('/')
def root():
    return dispatch('home')

@app.route('/<page>', methods=['GET'])
@limiter.limit(RATE_LIMIT)
def dispatch(page):
    print "Dispatching page in response to request: ", page

    num_requests = get_total_requests()
    return render_template('index.html', page=page, num_requests=num_requests)


@app.route('/bugreport_submit', methods=['POST'])
@limiter.limit(RATE_LIMIT)
def bug_report():
    bug_description = request.form['description']
    print "Processing bug report:\n\t", bug_description, "\n------ End of bug report ------"
    send_alert_email(bug_description, urgent=True)

    return dispatch('bugreport_success')


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
            return redirect(url_for('root', page='home', signedup='true'))
        else:
            return redirect(url_for('root', page='home', signedup='false'))


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
    result = clients.update({'client_id': client_id}, {'$inc': {'requests': 1}, '$push': {'activity': {'endpoint': endpoint, 'timestamp': timestamp}}})
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
    result = clients.update({'client_id': client_id}, {'$set': {'valid': False}})
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    return False

def validate_client(client_id):
    ''' Validate a client, enabling future access
        Return True if client's access mode was modified to True, or 
            return False if client's access mode was already True or
            the operation was unsuccessful
    '''
    result = clients.update({'client_id': client_id}, {'$set': {'valid': True}})
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    return False



