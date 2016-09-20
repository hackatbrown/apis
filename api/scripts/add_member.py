from api import db

api_members = db.members


def add_member(about, name, imageurl):
    new_member = {
        'name': name,
        'about': about,
        'image_url': imageurl
    }
    api_members.insert(new_member)
    return True
