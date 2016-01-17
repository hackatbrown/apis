from datetime import datetime
from sys import argv
from uuid import uuid4

from api import db

# The maximum number of Client IDs per student email address.
MAX_IDS_PER_STUDENT = 1

# simplify collection name
clients = db.clients

def add_client_id(email, username, client_id=None):
    if email[-10:] != '@brown.edu':
        print("Invalid student email")
        return None
    if clients.find({'client_email': email}).count() >= MAX_IDS_PER_STUDENT:
        print("Student email is already associated with 1 or more IDs")
        return None
    if not client_id:
        client_id = str(uuid4())
    while clients.find_one({'client_id': client_id}):
        client_id = str(uuid4())
    new_client = {
                  'client_id': client_id,
                  'username': username,
                  'client_email': email,
                  'joined': str(datetime.now()),
                  'valid': True
                 }
    clients.insert(new_client)
    return client_id

if __name__ == '__main__':
    if len(argv) < 3 or len(argv) > 4:
        print("Usage:  python -m api.scripts.add_client <client_email> <username> [client_id]")
        print("\tclient_email - Required. An @brown.edu email address.")
        print("\tusername - Required. A user who owns this client (typically a first and last name, like 'Josiah Carberry').")
        print("\tclient_id - Optional. Provide a string representation of a UUID4 client ID.")
        exit()
        
    if len(argv) == 3:
        client_id = add_client_id(argv[1], argv[2])
    if len(argv) == 4:
        client_id = add_client_id(argv[1], argv[2], client_id=argv[3])

    if not client_id:
        print("Email is not a Brown address. Unable to add client to database.")
    else:
        print("Client ID: ", client_id)
