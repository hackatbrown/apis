from api import db

api_documentations = db.api_documentations

def add_documentation(contents, name, urlname, imageurl):
    new_documentation = {
            'name': name,
            'urlname': urlname,
            'contents': contents,
            'imageurl': imageurl
            }
    api_documentations.insert(new_documentation)
    return True
