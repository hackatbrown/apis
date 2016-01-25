from flask import request, jsonify, Response
from api import app, db, make_json_error, support_jsonp
from api.meta import is_valid_client, log_client, INVALID_CLIENT_MSG

from datetime import datetime, date, timedelta

import functools

import json
import urllib

from api.scripts.coursemodels import *


# Created Index with: db.banner_course.createIndex( { "instructors.name": 1})

connect('brown')

PAGINATION_LIMIT = 10
PAGINATION_MAX = 42 #TODO: Make this do something.

@app.route('/courses')
@support_jsonp
def courses_index():
    return jsonify(paginate({}))


@app.route('/courses/<course_id>')
@support_jsonp
def course_specified(course_id):
    ''' Endpoint for all courses find requests (see public docs for documentation) '''
    if "-" in course_id:
        # Particular section or lab specificied
        res = BannerCourse.objects(full_number=course_id).first()
        if res == None:
            return make_json_error("No section found.") #TODO: Standardize error messages
        return jsonify(json.loads(res.to_json()))
    else:
        ans = paginate({"number":course_id})
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
    ans = paginate({"instructors__name": instructor_name})
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
    ans = paginate({"dept__code":dept_code})
    return jsonify(ans)


@app.route('/schedule')
@support_jsonp
def schedule_time():
    day = request.args.get('day','')
    time = request.args.get('time','')
    return check_against_time(day, time, time)

@app.route('/non-conflicting')
@support_jsonp
def non_conflicting():
    course = request.args.get('courses','')
    # MONGO QUERY: db.banner_course.find({meeting: {$all: [{$elemMatch: {"start_time": {$gte: 37200}}}]}})
    print(course)
    course_obj = BannerCourse.objects(full_number=course).first()
    print(course_obj)
    meetings = course_obj.meeting
    query = []
    f
    query.append({"$elemMatch": {"day_of_week": {"$ne": meetings[0].day_of_week}}})
    print(query)
    #res = BannerCourse.objects().filter(Q(meeting__all__day_of_week__ne="R")])
    res = BannerCourse.objects(__raw__={"meeting": {"$all": query}})
    return jsonify(items=[json.loads(elm.to_json()) for elm in res])



def check_against_time(day, stime, etime, concurrent=True):
    # print(time)
    # res = BannerCourse.objects(meeting__start_time__lte=time, meeting__end_time__gte=time, days_of_week=day)
    if concurrent:
        res = BannerCourse.objects().filter(meeting__days_of_week=day, meeting__match={"start_time__lte": etime, "end_time__gte": stime})
    else:
        res = BannerCourse.objects().filter(meeting__days_of_week=day, meeting__match={"start_time__gte": etime, "end_time__lte": stime})
    return jsonify(items=[json.loads(elm.to_json()) for elm in res])



# Helper methods

# TODO add any helper methods (methods that might be useful for multiple endpoints) here

def paginate(query_args):
    offset = request.args.get('offset', '')
    limit = int(request.args.get('limit', PAGINATION_LIMIT))
    print(offset)
    print(limit)
    if offset != '':
        res = BannerCourse.objects(id__gt=offset, **query_args)[:limit+1]
    else:
        res = BannerCourse.objects(**query_args)[:limit+1]

    next_url = "null"
    if len(res) == limit+1:
        next_url = request.base_url + "?" + urllib.parse.urlencode({"limit": limit, "offset": res[limit- 1].id})
    ans = {"href": request.url,
            "items": [json.loads(elm.to_json()) for elm in res],
            "limit": limit,
            "next": next_url,
            "offset": offset}
    return ans



def jsonify_mongoengine(json_data):
    rv = Response(
        (json_data,
         '\n'),
        mimetype='application/json')
    return rv
