from flask import request, jsonify, Response
from api import app, db, make_json_error, support_jsonp
from api.meta import is_valid_client, log_client, INVALID_CLIENT_MSG

from datetime import datetime, date, timedelta

import threading,sys

import json
import urllib
from collections import defaultdict
from tqdm import *

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
        res = BannerCourse.objects(full_number=course_id, **filter_semester({})).first()
        if res == None:
            return make_json_error("No section found.") #TODO: Standardize error messages
        return jsonify(json.loads(res.to_json()))
    else:
        ans = paginate(filter_semester({"number":course_id}))
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
    ans = paginate(filter_semester({"instructors__name": instructor_name}))
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
    ans = paginate(filter_semester({"dept__code":dept_code}))
    return jsonify(ans)


@app.route('/schedule')
@support_jsonp
def schedule_time():
    day = request.args.get('day','')
    time = int(request.args.get('time',''))
    res = check_against_time(day, time, time)
    return jsonify(items=[json.loads(elm.to_json()) for elm in res])

@app.route('/non-conflicting')
@support_jsonp
def non_conflicting():
    courses = request.args.get('courses','').split(",")
    if collision_calc_event.is_set():
        print("FANCY TABLE")
        available_set = None
        for course_number in courses:
            course = BannerCourse.objects(full_number=course_number).first().id
            if available_set is None:
                # ans = set(BannerCourse.objects().filter(id__in=CTable[course]))
                available_set = set(CTable[course])
            else:
                # ans = set.intersection(ans, set(BannerCourse.objects().filter(id__in=CTable[course])))
                available_set = set.intersection(available_set, CTable[course])
        query_args = {"id__in": list(available_set)}
    else:
        # 4.9s
        print("OLD WAY")
        conflicting_list = set()
        for c_id in courses:
            course = BannerCourse.objects(full_number=c_id).first()
            for m in course.meeting:
                res = check_against_time(m.day_of_week, m.start_time, m.end_time)
                conflicting_list.update(res)

        query_args = {"id__nin": [c.id for c in conflicting_list]}
        # ans = BannerCourse.objects().filter(id__nin=[c.id for c in conflicting_list]) 
    ans = paginate(query_args, {"courses": request.args.get('courses','')})
    #return jsonify(items=[json.loads(elm.to_json()) for elm in ans])
    return jsonify(ans)



def check_against_time(day, stime, etime):
    # print(time)
    # res = BannerCourse.objects(meeting__start_time__lte=time, meeting__end_time__gte=time, days_of_week=day)
    res = BannerCourse.objects().filter(meeting__day_of_week=day, meeting__match={"start_time__lte": etime, "end_time__gte": stime})
    return res



# Helper methods

# TODO add any helper methods (methods that might be useful for multiple endpoints) here

collision_calc_event = threading.Event()
CTable = defaultdict(list) #Ends up being a ~50kb

def calculate_collisions(event):
    # Experimental: Warning
    
    def is_collision(o1,o2):
        for m1 in o1.meeting:
            for m2 in o2.meeting:
                if m1.day_of_week ==m2.day_of_week:
                    #Now if times collide
                    # No Collision if
                    if not(m1.start_time <= m2.end_time and m1.end_time >= m2.start_time):
                        return False
        return True
    objs = BannerCourse.objects()
    for obj1 in tqdm(objs):
        for obj2 in objs:
            if obj1 != obj2 and not is_collision(obj1, obj2):
                CTable[obj1.id].append(obj2.id)
                CTable[obj2.id].append(obj1.id)
    print(sys.getsizeof(CTable))
    event.set()

collision_thread = threading.Thread(target=calculate_collisions, args=(collision_calc_event,))

collision_thread.start()

def paginate(query_args, params=None):
    '''
    Paginates the reuslts of a mongoengine query,
    query_args:: A dictionary of kwargs to include in the query
    '''
    offset = request.args.get('offset', None)
    limit = int(request.args.get('limit', PAGINATION_LIMIT))
    if limit <=0: limit = PAGINATION_LIMIT
    if offset is not None:
        query_args['id__gt'] = offset
    res = BannerCourse.objects(**query_args)[:limit+1]
    next_url = "null"
    if len(res) == limit+1:
        next_url = request.base_url + "?" + urllib.parse.urlencode({"limit": limit, "offset": res[limit- 1].id})
        if params is not None:
            next_url = next_url+"&"+urllib.parse.urlencode(params)
    ans = {"href": request.url,
            "items": [json.loads(elm.to_json()) for elm in res],
            "limit": limit,
            "next": next_url,
            "offset": offset}
    return ans

def filter_semester(query_args):
    if "semester" not in query_args:
        query_args['semester'] = gen_current_semester()
        return query_args
    return query_args

#TODO: The scraper uses this exact function. Can we have them use the same
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
