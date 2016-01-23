from flask import request, jsonify, Response
from api import app, db, make_json_error, support_jsonp
from api.meta import is_valid_client, log_client, INVALID_CLIENT_MSG

from datetime import datetime, date, timedelta

import json
import urllib

from api.scripts.coursemodels import *


# Created Index with: db.banner_course.createIndex( { "instructors.name": 1})

connect('brown')

DEFAULT_LIMIT = 10

@app.route('/courses')
@support_jsonp
def courses_index():
    '''
    client_id = request.args.get('client_id', 'missing_client')
    if is_valid_client(client_id):
            log_client(client_id, '/courses', str(datetime.now()))
    else:
            return make_json_error(INVALID_CLIENT_MSG)
    '''
    offset = request.args.get('offset', '')
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    assert(limit > 0)
    # total = len(BannerCourse.objects)
    if offset != '':
        res = BannerCourse.objects(id__gt=offset)[:limit+1]
    else:
        res = BannerCourse.objects()[:limit+1]
    next_url = "null"
    if len(res) == limit+1:
        next_url = request.base_url + "?" + urllib.parse.urlencode({"limit": limit, "offset": res[limit- 1].id})
    ans = {"href": request.url,
            "items": [json.loads(elm.to_json()) for elm in res],
            "limit": limit,
            "next": next_url,
            "offset": offset}
    return jsonify(ans)


@app.route('/courses/<course_id>')
@support_jsonp
def course_specified(course_id):
    ''' Endpoint for all courses find requests (see public docs for documentation) '''
    '''
    client_id = request.args.get('client_id', 'missing_client')
    if is_valid_client(client_id):
            log_client(client_id, '/wifi/count', str(datetime.now()))
    else:
            return make_json_error(INVALID_CLIENT_MSG)
    '''
    offset = request.args.get('offset', '')
    limit = int(request.args.get('limit', '1'))
    assert(limit > 0)

    if "-" in course_id:
        # Particular section or lab specificied
        res = BannerCourse.objects(full_number=course_id).first()
        if res == None:
            return make_json_error("No section found.") #TODO: Standardize error messages
        return jsonify(json.loads(res.to_json()))
    else:
        # Get all sections and labs
        if offset != '':
            res = BannerCourse.objects(number=course_id, id__gt=offset)[:limit+1]
        else:
            res = BannerCourse.objects(number=course_id)[:limit+1]
        next_url = "null"
        if len(res) == limit+1:
            next_url = request.base_url + "?" + urllib.parse.urlencode({"limit": limit, "offset": res[limit - 1].id})
        ans = {"href": request.url,
                "items": [json.loads(elm.to_json()) for elm in res],
                "limit": limit,
                "next": next_url,
                "offset": offset}
        return jsonify(ans)

@app.route('/instructors')
@support_jsonp
def instructors_index():
    ''' Endpoint for all instructors '''
    # TODO: Query Semester Limitations, perhaps abstract this?
    res = BannerCourse.objects().distinct("instructors.name")
    return jsonify(items=res)

@app.route('/instructors/<instructor_name>')
@support_jsonp
def instructors_specified(instructor_name):
    ''' Endpoint for a given instructor '''
    # TODO: Query Semester Limitations, perhaps abstract this?
    offset = request.args.get('offset', '')
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    if offset != '':
        res = BannerCourse.objects(id__gt=offset, instructors__name=instructor_name)[:limit+1]
    else:
        res = BannerCourse.objects(instructors__name=instructor_name)[:limit+1]

    next_url = "null"
    if len(res) == limit+1:
        next_url = request.base_url + "?" + urllib.parse.urlencode({"limit": limit, "offset": res[limit- 1].id})
    ans = {"href": request.url,
            "items": [json.loads(elm.to_json()) for elm in res],
            "limit": limit,
            "next": next_url,
            "offset": offset}
    return jsonify(ans)

@app.route('/departments')
@support_jsonp
def departments_index():
    # MONGO CMD: db.banner_course.aggregate([{$group: {"_id": {dept: "$dept"}}}])
    res = BannerCourse._get_collection().aggregate([{"$group": {"_id": "$dept"}}])
    val = [elm.get('_id') for elm in res]
    return jsonify(items=val)

@app.route('/departments/<dept_code>')
@support_jsonp
def departments_specified(dept_code):
    ''' Endpoint for a given department '''
    #res = BannerCourse.objects(dept
    return ""

# Helper methods

# TODO add any helper methods (methods that might be useful for multiple endpoints) here


def jsonify_mongoengine(json_data):
    rv = Response(
        (json_data,
         '\n'),
        mimetype='application/json')
    return rv
