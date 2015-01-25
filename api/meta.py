from flask import jsonify
from api import app, db

# simplify collection names
clients = db.clients

@app.route('/')
def root():
	return jsonify(hello='world')



# Helper methods

def is_valid_client(client_id):
	''' Return True if client ID is valid, False otherwise '''
	client = clients.find_one({'client_id': client_id})
	if client and valid in client and client['valid']:
		# client exists in database and is marked as valid
		return True
	return False

def log_client(client_id, activity, timestamp):
	''' Log a client's activity with the time of occurence '''
	result = clients.update({'client_id': client_id}, {'$inc': {'requests': 1}, '$push': {'activities': {'activity': activity, 'timestamp': timestamp}}})
	if 'nMatched' in result and result['nMatched'] == 1:
		return True
	return False


