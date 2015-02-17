from flask import jsonify, render_template, url_for
from api import app, db, limiter, RATE_LIMIT

'''
db.clients contains documents of the form:
{ 
  'client_id': str,
  'client_name': str,       <-- user-defined name for client
  'requests': int,
  'joined': str,            <-- ISO Format
  'activity': [ 
                { 
                  'endpoint': str, 
                  'timestamp': str      <-- ISO Format
                } 
              ],
  'valid': boolean
}

'''

# simplify collection names
clients = db.clients

@app.route('/')
@limiter.limit(RATE_LIMIT)
def root():
    return render_template('documentation.html')



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
    print "Client ID", client_id, "not found in client collection" 
    return False

def log_client(client_id, endpoint, timestamp):
    ''' Log a client's activity with the time of occurence 
        Return True if successfully logged, otherwise False
    '''
    result = clients.update({'client_id': client_id}, {'$inc': {'requests': 1}, '$push': {'activity': {'endpoint': endpoint, 'timestamp': timestamp}}})
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    print "Bad result from log_client: ", result
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



