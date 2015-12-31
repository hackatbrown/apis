from api import db

api_documentations = db.api_documentations

def add_documentation(contents, name):
    new_documentation = {
            'name': name,
            'contents': contents
            }
    api_documentations.insert(new_documentation)
    return True
