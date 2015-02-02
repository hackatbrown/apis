from flask import jsonify
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
    return jsonify(hello='world')



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
    ''' Log a client's activity with the time of occurence '''
    result = clients.update({'client_id': client_id}, {'$inc': {'requests': 1}, '$push': {'activity': {'endpoint': endpoint, 'timestamp': timestamp}}})
    if u'nModified' in result and result[u'nModified'] == 1:
        return True
    print "Bad result from log_client: ", result
    return False



