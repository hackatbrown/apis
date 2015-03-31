from datetime import datetime
from sys import argv
from uuid import uuid4

from api import db

# simplify collection name
clients = db.clients

def add_client_id(client_name, email, username, client_id=None):
    if clients.find_one({'client_name': client_name}):
        return None
    if email[-10:] != '@brown.edu':
        return None
    if not client_id:
        client_id = str(uuid4())
    new_client = {
                  'client_id': client_id,
                  'client_name': client_name,
                  'username': username,
                  'client_email': email,
                  'joined': str(datetime.now()),
                  'valid': True
                 }
    clients.insert(new_client)
    return client_id

if __name__ == '__main__':
    if len(argv) < 2 or len(argv) > 3:
        print "Usage:  python -m api.scripts.add_client <client_name> <client_email> <username> [client_id]"
        print "\tclient_name - Required. A string nickname for this client. (Wrap in quotes if spaces.)"
        print "\tclient_email - Required. An @brown.edu email address."
        print "\tusername - Required. A user who owns this client (typically a first and last name, like 'Josiah Carberry')."
        print "\tclient_id - Optional. Provide a string representation of a UUID4 client ID."
        exit()
        
    if len(argv) == 4:
        client_id = add_client_id(argv[1], argv[2], argv[3])
    if len(argv) == 5:
        client_id = add_client_id(argv[1], argv[2], argv[3], client_id=argv[4])

    if not client_id:
        print "Client name taken or email is not a Brown address. Unable to add client to database."
    else:
        print "Client ID: ", client_id