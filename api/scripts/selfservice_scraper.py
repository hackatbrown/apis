# from bs4 import BeautifulSoup
import argparse
import os
import re
import sys
from copy import deepcopy
from datetime import date,datetime
from itertools import zip_longest
from pprint import pprint
from queue import Queue
from threading import Thread
# from time import time

import bs4
import requests
from tqdm import *

from mongoengine import *

# TODO: Only local
connect('brown')


class CourseMeeting(EmbeddedDocument):
    days_of_week = ListField(StringField(max_length=1))
    start_time = StringField()
    end_time = StringField()
    duration = ListField(StringField())
    location = StringField()


# TODO: What is the best way to do this? References?
class CourseInstructor(EmbeddedDocument):
    name = StringField()
    email = StringField()
    isPrimary = BooleanField()


class BannerCourse(DynamicDocument):
    creation_date = DateTimeField()
    number = StringField(required=True)
    dept = StringField(required=True, min_length=4, max_length=4)
    title = StringField(required=True)
    seats_available = IntField()
    seats_total = IntField()
    meeting = ListField(EmbeddedDocumentField(CourseMeeting))
    description = StringField(required=True)
    instructors = ListField(EmbeddedDocumentField(CourseInstructor))
    prerequisites = StringField()
    exam_time = StringField()
    exam_date = StringField()
    exam_location = StringField()
    exam_group = StringField()
    critical_review = StringField()

    def save(self, *args, **kwargs):
        if not self.creation_date:
            self.creation_date = datetime.now()
        return super(BannerCourse, self).save(*args, **kwargs)


'''
# Debugging HTTP Errors can be tough
# Uncomment this to debug requests and see everything

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client

http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
'''

def grouper(iterable, n, fillvalue=None):
    """
    Groups items from iterable into groups of n with a fill of None
    :param iterable: the source
    :param n: the size of the group
    :param fillvalue: Fill a partial group with these
    :return: tuple of length n
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


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


def gen_next_semester(semester_string):
    """
    Given a semester string, generates the next
    valid semester to occur.

    e.g "Fall 2015" => "Spring 2016"
    """
    season, year = semester_string.split()
    year = int(year)
    if season.lower() == "fall":
        return "Spring " + str(year + 1)
    if season.lower() == "spring":
        return "Summer " + str(year)
    if season.lower() == "summer":
        return "Fall " + str(year)
    else:
        return None


def generate_semesters(n):
    """
    Generates n semester strings, starting
    from the current semester.

    I/P: An integer, n, s.t n >= 1
    O/P: A list of length n whose elements are
    the upcoming semesters in order (including
    the current semester)
    """
    semesters = []
    semesters.append(gen_current_semester())
    for i in range(1, n):
        semesters.append(gen_next_semester(semesters[i-1]))
        return semesters

Semesters = generate_semesters(3)
Departments = ['AFRI', 'AMST', 'ANTH', 'APMA', 'ARAB', 'ARCH', 'ASYR',
               'BEO', 'BIOL', 'CATL', 'CHEM', 'CHIN', 'CLAS', 'CLPS',
               'COLT', 'CROL', 'CSCI', 'CZCH', 'DEVL', 'EAST', 'ECON',
               'EDUC', 'EGYT', 'EINT', 'ENGL', 'ENGN', 'ENVS', 'ERLY',
               'ETHN', 'FREN', 'GEOL', 'GNSS', 'GREK', 'GRMN', 'HIAA',
               'HISP', 'HIST', 'HMAN', 'HNDI', 'INTL', 'ITAL', 'JAPN',
               'JUDS', 'KREA', 'LAST', 'LATN', 'LING', 'LITR', 'MATH',
               'MCM', 'MDVL', 'MED', 'MES', 'MGRK', 'MUSC', 'NEUR', 'PHIL',
               'PHP', 'PHYS', 'PLCY', 'PLME', 'PLSH', 'POBS', 'POLS',
               'PRSN', 'RELS', 'REMS', 'RUSS', 'SANS', 'SCSO', 'SIGN',
               'SLAV', 'SOC', 'SWED', 'TAPS', 'TKSH', 'UNIV', 'URBN',
               'VISA']

def _semester_to_value(semester_string):
    """
    Converts a Semester String to its numeric representation.

    [SelfserviceSession._semester_to_value(s) for s in ['Spring 2015', 'Summer 2015',
                                          'Fall 2015', 'Spring 2016']]
    [201420, 201500, 201510, 201520]
    """
    words = semester_string.split(' ')
    assert(len(words) == 2)
    assert(int(words[1]) > 2010)  # Not really needed.
    res = int(words[1]) * 100
    if words[0] == 'Fall':
        res += 10
    elif words[0] == 'Spring':
        res -= 100
        res += 20
    elif words[0] == 'Summer':
        pass
    else:
        print("ERROR: Unidentified Semester")
    return res

def _value_to_semester(value):
    """
    Converts a numeric representation of a semester to a String.
    >>> [ SelfserviceSession._value_to_semester(v) for v in [201420, 201500, 201510, 201520]]
    ['Spring 2015', 'Summer 2015', 'Fall 2015', 'Spring 2016']
    """
    year = int(value[:4])  # Get Year
    season = value[-2:]
    if season == "00":
        return str(year) + " Summer"
    elif season == "10":
        return str(year) + " Fall"
    elif season == "20":
        return str(year + 1) + " Spring"
    else:
        print("ERROR: Unidentified Semester")



class SelfserviceSession:
    '''
    Used to obtain course information from self service. This session object
    holds repeated request headers and is a wrapper for the requests Session
    object which manages cookies.
    '''

    # The standard headers for sending a request.
    # Typically you'll add a Referer.
    BaseHeaders = {
        'User-Agent': ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                       "(KHTML, like Gecko) Ubuntu Chromium/43.0.2357.130"
                       "Chrome/43.0.2357.130 Safari/537.36"),
        'Accept': ('text/html,application/xhtml+xml,'
                   'application/xml;q=0.9,image/webp,*/*;q=0.8'),
        'Origin': 'https://selfservice.brown.edu'
    }

    def __init__(self, username, password):
        self.s = None
        self.username = username
        self.password = password
        self.logged_in = self.login()

    def get_base_headers(self):
        return deepcopy(self.BaseHeaders)

    def login(self):
        '''
        Creates a new object which stores the cookie and header information
        using the requests Session object.
        '''
        url = ("https://selfservice.brown.edu/"
               "ss/twbkwbis.P_GenMenu?name=bmenu.P_MainMnu")
        login_url = "https://selfservice.brown.edu/ss/twbkwbis.P_ValLogin"
        headers = self.get_base_headers()
        headers['Referer'] = url

        payload = {
            'sid': self.username,
            'PIN': self.password
        }
        self.s = requests.Session()
        self.s.get(url)  # Get session id/cookies
        res = self.s.post(login_url, data=payload, headers=headers,
                    allow_redirects=True)

        if 'Invalid login information' in res.text:
            return False
        return True


def gen_courses( ss, semester, dept):
    """
    A generator for courses of a particular semester and department
    :return: course details to be processed by other threads
    """
    visited = set()  # This may not be necessary
    for results_page in _gen_search_results_soup(ss, semester, dept):
        for course_details in _courses_on_page(results_page):
            if not course_details[1] in visited:
                #yield _extract_course(ss, course_details)
                yield course_details
                visited.add(course_details[1])


def _gen_search_results_soup(ss, semester, department):
    """
    Generates a 'BeautifulSoup' for each page in the results of
    searching through all the courses by semester and department.
    This is called by gen_courses().
    """
    url = 'https://selfservice.brown.edu/ss/hwwkcsearch.P_Main'
    payload = {
        'IN_TERM': _semester_to_value(semester),
        'IN_SUBJ': department,
        'IN_SUBJ_multi': department,
        'IN_TITLE': '',
        'IN_INST': '',
        'IN_CRSE': '',
        'IN_ATTR': 'ALL',
        'IN_INDP': 'on',
        'IN_HOUR': '',
        'IN_DESCRIPTION': '',
        'IN_CREDIT': 'ALL',
        'IN_DEPT': 'ALL',
        'IN_METHOD': 'S',
        'IN_CRN': '',
    }

    headers = ss.get_base_headers()
    headers['Referer'] = url
    current = 1

    requests.utils.add_dict_to_cookiejar(ss.s.cookies,
                                         {'L_PAGE887098': str(current)})

    r = ss.s.post(url, data=payload, headers=headers)
    s = bs4.BeautifulSoup(r.content, 'html.parser')
    # max_page = len(s.select("#SearchResults")[0].select('a')) - 1
    set_results_string = s.select('img[onload^=setResults2]')
    if len(set_results_string) == 0:  # No Classes
        return
    set_results_string = set_results_string[0]['onload']
    max_page = int(set_results_string[12:-1].split(',')[0])
    yield s  # Page 1
    current += 1
    while current <= max_page:
        requests.utils.add_dict_to_cookiejar(
            ss.s.cookies, {'L_PAGE887098': str(current)})

        r = ss.s.post(url, data=payload, headers=headers)
        s = bs4.BeautifulSoup(r.content, 'html.parser')
        yield s
        current += 1

def _courses_on_page(page):
    """
    Given a page (BeautifulSoup), this method parses out couses which
    appear on the page.
    Called by gen_courses.
    """
    courses = [c['onclick'] for c in
               page.select('td[onclick^="Show_Detail"]')]

    args = [c[13:-3].split("','") for c in courses]
    return args

def _extract_course(ss, args):
    '''
    Given the args which reprsent the course in the source code of
    banner in a tuple, this method should produce some object or
    dictionary of data to be added to the database. This is the last
    step.
    Called by gen_courses()
    '''
    url = 'https://selfservice.brown.edu/ss/hwwkcsearch.P_Detail'
    payload = {
        'IN_TERM': args[0],
        'IN_CRN': args[1],
        'IN_FROM': '3',
    }

    headers = ss.get_base_headers()
    headers['Referer'] = ("https://selfservice.brown.edu"
                          "/ss/hwwkcsearch.P_Main")

    r = ss.s.post(url, data=payload, headers=headers)
    info = bs4.BeautifulSoup(r.content, 'html5lib')
    course = BannerCourse()
    course_soup = info.select("#CourseDetailx")[0]

    for shit in course_soup.select('img.headerImg'):
        shit.replace_with('')

    course['number'] = course_soup.contents[0].contents[1]\
        .contents[0].find_all()[0].text
    course['dept'] = course['number'][:4]
    course['title'] = course_soup.contents[0].contents[1]\
        .contents[0].find_all('td')[1].text


    add_dict(course, _extract_course_seats(course_soup))

    res = _extract_course_meeting(course_soup)['meeting']
    if res != None:
        course.meeting = [CourseMeeting(**meeting) for meeting in res]

    add_dict(course, _extract_course_description(course_soup))

    res = _extract_course_instructors(course_soup)
    if res != None:
        course.instructors = [CourseInstructor(**instructor) for instructor in res]

    add_dict(course, _extract_course_prerequisites(course_soup))

    add_dict(course, _extract_course_exam_info(course_soup))

    course['critical_review'] = course_soup\
        .find_all('a', text="Critical Review")[0]['href']

    # Book data seems nigh impossible. Seldom is it present,
    # so I would need to write the scraper then.
    #course_data.update(_extract_course_books(course_soup))

    return course


def add_dict(course, dict):
    for k in dict.keys():
        course[k] = dict[k]


def _extract_course_seats(course_soup):
    seats_data = {}
    seats_split = course_soup.table.tbody.find_all('tr')[3].text.split(" ")
    try:
        seats_data['seats_available'] = int(seats_split[0])
        seats_data['seats_total'] = int(seats_split[2])
    except ValueError:
        return {}
    return seats_data


def _extract_course_description(course_soup):
    return {'description': course_soup.select("#div_DESC")[0].text[2:]}


def _extract_course_instructors(course_soup):
        instructor_data = course_soup.select('td.resultstable')[0]
        if 'TBA' in instructor_data.contents[1]:
            return None
        ans = []
        contents = instructor_data.contents
        assert(len(contents) > 4)
        prof = {}
        prof['name'] = contents[0].replace('(', '').strip()
        prof['email'] = contents[3]['href'][7:]
        prof['isPrimary'] = (contents[1].text == "P")
        ans.append(prof)
        if contents[4] != '\n':
            for group in grouper(contents[4:],2):
                if group[0] == '\n' or group[1] == '\n':
                    break
                prof = {}
                prof['name'] = group[0].strip()
                prof['email'] = group[1]['href'][7:]
                prof['isPrimary'] = False
                ans.append(prof)
        return ans


def parse_schedule(schedule):
    words = schedule.split()[2:]
    days = [list(w) for w in words[:-5]]
    days = [str(item) for sublist in days for item in sublist] # Flatten list
    time = ' '.join(words[-5:]).split(' - ')
    return {'days_of_week': days, 'start_time': time[0], 'end_time': time[1]}


def parse_duration(duration):
    words = duration.split(' ')
    return words[1], words[3]


def _extract_course_meeting(course_html):
    """
    :param course_html: The soup of the page
    :return: a list of all meeting times
    """
    data = course_html.find_all(text=re.compile("Primary Meeting:"))
    if len(data) == 0:
        return {'meeting': None}
    data = [d for d in data[0].parent.contents if d.name != 'br']
    ans = []
    i = 0
    while i < len(data):
        meeting = {}
        meeting.update(parse_schedule(data[i]))
        i += 1
        # meeting['duration'] = None
        if (data[i]).startswith('From:'):
            meeting['duration'] = parse_duration(data[i])
            i += 1
        meeting['location'] = str(data[i])
        i += 1
        ans.append(meeting)
    return {'meeting': ans}


def _extract_course_prerequisites(course_soup):
    """
    Extracts the prereqs for the given course
    :param course_soup: the soup containing course info
    :return: a dictionary containing a 'prerequisites' entry
    """
    reg = re.compile(r'Prerequisites')
    prereq_elements = [e for e in course_soup.find_all('b') if reg.match(e.text)]
    if len(prereq_elements) > 0:
        return {'prerequisites': prereq_elements[0].parent.contents[2].strip()}
    return {}

def format_key(key):
    return key.strip().replace(' ','_').replace(':','').lower()

def _extract_course_exam_info(course_soup):
    '''
    Extracts exam date,time,group,location,etc. if present for the given course
    :param course_soup: the soup containing course info
    :return: a dictionary containing separate entries per exam info.
            Location information is a single entry of a list of tuples
    '''
    exam_data = {}
    reg = re.compile('Exam Information')
    exam_info = course_soup.find_all('b', text=reg)
    if len(exam_info) > 0:
        res_tables = exam_info[0].parent.select('table.resultstable')
        if len(res_tables) >= 2:
            exam_info = res_tables[1]
            if "Please contact" not in exam_info.text and "Not Assigned" not in exam_info.text:
                tds = exam_info.find_all('td')
                for key, val in grouper(tds, 2):
                    exam_data[format_key(key.text)] = val.text
            else:
                # Odd case where only the Exam Group is present
                exam_data['exam_group'] = exam_info.find('td').text.split(":")[1].strip()
        if len(res_tables) >=3:
            # If exam location information present
            location_info = []
            more_exam_info_rows = res_tables[2].find_all('tr')[1:]
            for row in more_exam_info_rows:
                location_info.append([entry.text for entry in row.find_all('td')])
            exam_data['exam_location'] = location_info
    return exam_data


class CourseExtractionWorker(Thread):
    """
    Given course details, downloads and extracts information for that course
    """
    def __init__(self, queue, session, to_files):
        Thread.__init__(self)
        self.queue = queue
        self.session = session
        self.to_files = to_files

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple?
            path, semester, course_details = self.queue.get()
            course = _extract_course(self.session, course_details)
            if self.to_files:
                # Save Course
                fpath = path + semester + '/' + course['number'] + '.txt'
                with open(fpath, 'w+') as fd:
                    pprint(course, fd)
            else:
                #print(course)
                #courseObj = BannerCourse(**course)
                course.save()
            self.queue.task_done()


def main():
    '''
    Main Function
    '''

    parser = argparse.ArgumentParser(description='Scrape course information from Banner.')
    parser.add_argument('--user-and-pass', nargs=2, metavar=('USER','PASS'), required=True)
    parser.add_argument('--to-files', nargs=1, metavar='PATH',
                        help='Save files in given directory; otherwise print to stdout.')

    args = parser.parse_args()

    username = getattr(args, 'user_and_pass')[0]
    passwd = getattr(args, 'user_and_pass')[1]

    path = ""
    if args.to_files != None:
        path = str(os.path.expanduser(os.path.join(args.to_files[0],'')))
    s = SelfserviceSession(username, passwd)

    queue = Queue()
    for x in range(8):
        worker = CourseExtractionWorker(queue, s, (args.to_files != None))
        worker.daemon = True
        worker.start()

    for semester in Semesters:
        print("Current: "+semester, file=sys.stderr)
        if args.to_files != None: os.makedirs(path+semester, exist_ok=True)
        for department in tqdm(Departments, unit="Departments"):
            for course in gen_courses(s, semester, department):
                queue.put((path, semester, course))
    queue.join()

main()

