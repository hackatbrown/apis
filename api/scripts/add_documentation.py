from api import db

api_documentations = db.api_documentations

def add_documentation(contents, name, urlname):
    new_documentation = {
            'name': name,
            'urlname': urlname,
            'contents': contents
            }
    api_documentations.insert(new_documentation)
    return True
