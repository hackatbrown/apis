from flask import request, jsonify
from api import app, make_json_error, support_jsonp
from api.meta import is_valid_client, log_client, INVALID_CLIENT_MSG
from mongoengine import connect
import json
import urllib
from collections import defaultdict
import random
from api.scripts.coursemodels import *
import bson
from datetime import date


PREFIX = "/academic"
PAGINATION_LIMIT = 10
PAGINATION_MAX = 42
#TODO: Maybe there's some way to use the same connection as given by 'db'.
connect('brown')


@app.route(PREFIX + '/courses')
@support_jsonp
def courses_index():
    '''
    Returns all courses
    or
    Returns the sections ids specified
    '''
    arg_numbers = request.args.get('numbers',None)
    if arg_numbers is not None:
        numbers = []
        full_numbers = []
        for n in arg_numbers.split(","):
            if "-" in n:
                full_numbers.append(n)
            else:
                numbers.append(n)
        return jsonify(paginate(filter_semester({"$or": [{"full_number": {"$in": full_numbers}}, {"number": {"$in": numbers}}]}),raw=True))
    return jsonify(paginate(filter_semester({})))


@app.route(PREFIX + '/courses/<course_id>')
@support_jsonp
def course_specified(course_id):
    '''
    Either,
    * Returns the exact course/section (CSCI1760-S01)
    * or Returns all sections for that course (CSCI1760)
    '''
    if "-" in course_id:
        # Particular section or lab specificied
        res = BannerCourse.objects(full_number=course_id,
                                   **filter_semester({})).first()
        if res is None:
            return make_json_error("No section found.")
        return jsonify(json.loads(res.to_json()))
    else:
        ans = paginate(filter_semester({"number": course_id}))
        return jsonify(ans)


@app.route(PREFIX + '/instructors')
@support_jsonp
def instructors_index():
    ''' Endpoint for all instructors '''
    res = BannerCourse.objects().distinct("instructors.name")
    return jsonify(items=res)


@app.route(PREFIX + '/instructors/<instructor_name>')
@support_jsonp
def instructors_specified(instructor_name):
    ''' Endpoint for a given instructor '''
    ans = paginate(filter_semester({"instructors__name": instructor_name}))
    return jsonify(ans)


@app.route(PREFIX + '/departments')
@support_jsonp
def departments_index():
    '''Endpoint for unique departments as a list'''
    res = BannerCourse._get_collection()\
        .aggregate([{"$group": {"_id": "$dept"}}])
    val = [elm.get('_id') for elm in res]
    return jsonify(items=val)


@app.route(PREFIX + '/departments/<dept_code>')
@support_jsonp
def departments_specified(dept_code):
    ''' Endpoint for courses for a given department '''
    ans = paginate(filter_semester({"dept__code": dept_code}))
    return jsonify(ans)


# TODO: Think of a good end-point name
@app.route(PREFIX + '/during')
@support_jsonp
def schedule_time():
    '''Endpoint for courses ocurring during a given time'''
    day = request.args.get('day', None)
    if day is None:
        return make_json_error("Missing parameter: day")
    time = int(request.args.get('time', '-1'))
    if time < 0:
        return make_json_error("Invalid or Missing parameter: time")
    # res = check_against_time(day, time, time)
    query_args = {'meeting.day_of_week':day,
            "meeting.start_time": {'$lte': time},
            "meeting.end_time": {'$gte': time}}
    return jsonify(paginate(query_args, params={'day': day, 'time': time}, raw=True))
    # return jsonify(items=[json.loads(elm.to_json()) for elm in res])


@app.route(PREFIX + '/non-conflicting')
@support_jsonp
def non_conflicting():
    courses = request.args.get('numbers', '').split(",")
    if BannerCourse.objects().count() == NonconflictEntry.objects().count():
        # Precomputed faster method,
        available_set = None
        for course_number in courses:
            res = BannerCourse.objects(full_number=course_number)
            if len(res) <= 0:
                return make_json_error(\
                    "Invalid course section/lab/conference:"\
                    +course_number)
            course = res.first().id
            non_conflicting_list = NonconflictEntry.objects(course_id=course)
            if len(non_conflicting_list) <= 0:
                return make_json_error(\
                        "Error with course section/lab/conference:"\
                        +course_number)
            non_conflicting_list = non_conflicting_list.first().non_conflicting
            if available_set is None:
                available_set = set(non_conflicting_list)
            else:
                available_set = set.intersection(available_set,
                        non_conflicting_list)
        query_args = {"id__in": list(available_set)}
    else:
        # Slower method, a couple of seconds
        conflicting_list = set()
        for c_id in courses:
            course = BannerCourse.objects(full_number=c_id).first()
            for m in course.meeting:
                res = check_against_time(
                    m.day_of_week, m.start_time, m.end_time)
                conflicting_list.update(res)
        query_args = {"id__nin": [c.id for c in conflicting_list]}

    ans = paginate(query_args, {"numbers": request.args.get('numbers', '')})
    return jsonify(ans)


def check_against_time(day, stime, etime):
    res = BannerCourse.objects()\
        .filter(
            meeting__day_of_week=day,
            meeting__match={"start_time__lte": etime, "end_time__gte": stime})
    return res

# Helper methods


def paginate(query, params=None, raw=False):
    '''
    Paginates the reuslts of a mongoengine query,
    query:: A dictionary of kwargs to include in the query
    '''
    offset = request.args.get('offset', None)
    limit = int(request.args.get('limit', PAGINATION_LIMIT))
    limit = min(max(limit, 1), PAGINATION_MAX)
    if not raw:  # Make Raw
        query = BannerCourse.objects(**query)._query
    if offset is not None:
        if '_id' not in query:
            query['_id'] = {}
        query['_id']['$gt'] = bson.objectid.ObjectId(offset)
    res = list(BannerCourse.objects(__raw__=query).order_by('_id')[:limit+1])
    next_url = "null"
    if len(res) == limit+1:
        next_url = request.base_url + "?" +\
            urllib.parse.urlencode({"limit": limit,
                                    "offset": res[limit - 1].id})
        if params is not None:
            next_url = next_url+"&"+urllib.parse.urlencode(params)
        res.pop()

    if offset is None: offset = "null"
    ans = {"href": request.url,
           "items": [json.loads(elm.to_json()) for elm in res],
           "limit": limit,
           "next": next_url,
           "offset": offset}
    return ans


def filter_semester(query_args):
    ''' Given a query dictionary, modifies it for the current semester'''

    def is_valid(v):
        if v is None:
            return False
        words = v.split(" ")
        if words[0] not in ['Spring', 'Summer', 'Fall']:
            return False
        if int(words[1]) < 2000 or int(words[1]) > 2050:
            return False
        return True

    pvalue = request.args.get('semester', None)
    if is_valid(pvalue):
        query_args['semester'] = pvalue
    else:
        query_args['semester'] = gen_current_semester()
    return query_args


# TODO: The scraper uses this exact function. Can we have them use the same
# block of code instead of duplicates
def gen_current_semester():
    '''
    Generates the semester string for the current semester.
    This uses fixed months for each semester, which isn't exactly optimal.

    I/P: Nothing.
    O/P: A valid semester string "(Fall/Summer/Spring) YEAR"
    '''
    seasons = [("Spring ", {1, 2, 3, 4, 5}),
               ("Summer ", {6, 7}),
               ("Fall ", {8, 9, 10, 11, 12})]
    today = date.today()
    year = today.year
    month = today.month
    season_tuple = list(filter(lambda p: month in p[1], seasons))[0][0]
    return season_tuple + str(year)
