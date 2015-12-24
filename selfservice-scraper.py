# from bs4 import BeautifulSoup
import bs4
import requests
import re
from itertools import tee
from copy import deepcopy
from datetime import date
from pprint import pprint

import secret  # Passwords

'''
# Debugging HTTP Erros can be tough
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

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

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
    seasonTuple = list(filter(lambda p: month in p[1], seasons))[0][0]
    return seasonTuple + str(year)


def gen_next_semester(semester_string):
    '''
    Given a semester string, generates the next
    valid semester to occur.

    e.g "Fall 2015" => "Spring 2016"
    '''
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
    '''
    Generates n semester strings, starting
    from the current semester.

    I/P: An integer, n, s.t n >= 1
    O/P: A list of length n whose elements are
    the upcoming semesters in order (including
    the current semester)
    '''
    semesters = []
    semesters.append(gen_current_semester())
    for i in range(1, n):
        semesters.append(gen_next_semester(semesters[i-1]))
        return semesters


class SelfserviceSession():
    '''
    Used to obtain course information from self service. This session object
    holds repeated request headers and is a wrapper for the requests Session
    object which manages cookies.
    '''

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

    def get_base_headers(self):
        return deepcopy(self.BaseHeaders)

    @staticmethod
    def _semester_to_value(semester_string):
        '''
        >>> [ _semester_to_value(s) for s in ['Spring 2015', 'Summer 2015',
                                              'Fall 2015', 'Spring 2016']]
        [201420, 201500, 201510, 201520]
        '''
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

    @staticmethod
    def _value_to_semester(value):
        '''
        >>> [ __value_to_semester(v) for v in [201420, 201500, 201510, 201520]]
        ['Spring 2015', 'Summer 2015', 'Fall 2015', 'Spring 2016']
        '''
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

    def gen_courses(self, semester, dept):
        '''
        A generator for courses of a particular semester and department
        '''
        visited = set()  # This may not be necessary
        for results_page in self._gen_search_results_soup(semester, dept):
            print("RESULTS PAGE")
            for course_details in self._courses_on_page(results_page):
                if not course_details[1] in visited:
                    yield self._extract_course(course_details)
                    visited.add(course_details[1])

    def _gen_search_results_soup(self, semester, department):
        '''
        Generates a 'BeautifulSoup' for each page in the results of
        searching through all the courses by semester and department.
        This is called by gen_courses().
        '''
        url = 'https://selfservice.brown.edu/ss/hwwkcsearch.P_Main'
        payload = {
            'IN_TERM': SelfserviceSession._semester_to_value(semester),
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

        headers = self.get_base_headers()
        headers['Referer'] = url
        current = 1

        requests.utils.add_dict_to_cookiejar(self.s.cookies,
                                             {'L_PAGE887098': str(current)})

        r = self.s.post(url, data=payload, headers=headers)
        s = bs4.BeautifulSoup(r.content, 'html.parser')
        # maxPage = len(s.select("#SearchResults")[0].select('a')) - 1
        setResultsString = s.select('img[onload^=setResults2]')[0]['onload']
        maxPage = int(setResultsString[12:-1].split(',')[0])
        yield s  # Page 1
        current += 1
        while current <= maxPage:
            requests.utils.add_dict_to_cookiejar(
                self.s.cookies, {'L_PAGE887098': str(current)})

            r = self.s.post(url, data=payload, headers=headers)
            s = bs4.BeautifulSoup(r.content, 'html.parser')
            yield s
            current += 1

    def _courses_on_page(self, page):
        '''
        Given a page (BeautifulSoup), this method parses out couses which
        appear on the page.
        Called by gen_courses.
        '''
        courses = [c['onclick'] for c in
                   page.select('td[onclick^="Show_Detail"]')]

        args = [c[13:-3].split("','") for c in courses]
        return args

    @staticmethod
    def _get_first(iterable, default=None):
        ''' Courtesy of SO'''
        if iterable:
            for item in iterable:
                return item
        return default

    def _extract_course(self, args):
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

        headers = self.get_base_headers()
        headers['Referer'] = ("https://selfservice.brown.edu"
                              "/ss/hwwkcsearch.P_Main")

        r = self.s.post(url, data=payload, headers=headers)
        info = bs4.BeautifulSoup(r.content, 'html5lib')
        course_data = {}
        course_html = info.select("#CourseDetailx")[0]

        for shit in course_html.select('img.headerImg'):
            shit.replace_with('')
        #for moreshit in course_html.select('br'):
            #moreshit.replace_with('')

        # Goals
        course_data['number'] = course_html.contents[0].contents[1].contents[0].find_all()[0].text
        course_data['title'] = course_html.contents[0].contents[1].contents[0].find_all('td')[1].text

        print(course_data['number'])
        print(course_data['title'])
        seats_split = course_html.table.tbody.find_all('tr')[3].text.split(" ")
        course_data['seats_available'] = seats_split[0]
        course_data['seats_total'] = seats_split[2]
        # Do some classes have multiple meeting times? If so, I need an example in order to scrape it
        course_data['meeting'] = str(self._get_first(course_html.find_all(text=re.compile('Primary Meeting:'))))
        #for td in upper_table_rows[4].find_all('td'):
            #course_data['meeting'].append((td.contents[0], td.contents[2]))
        course_data['description'] = course_html.select("#div_DESC")[0].text
        course_data['instructors'] = []
        # Can do more parsing here, would need to pair strings with
        # emails, or maybe find out which professor is primary
        # I'm just grabbing email address for now
        instructor_data = course_html.select('td.resultstable')[0]
        for email in instructor_data.select('a'):
            course_data['instructors'].append(email['href'][7:])
        # Prereqs should be tested
        #lower_table_rows = course_html.find_all('tbody')[2].find_all('tr')
        #course_data['prerequisites'] = lower_table_rows[2].text
        # TODO: Test This

        reg = re.compile(r'Prerequisites')
        prereq_elements = [e for e in course_html.find_all('b') if reg.match(e.text)]
        if len(prereq_elements) > 0:
            course_data['prerequisites'] = prereq_elements[0].parent.contents[2].strip()

        exam_info = course_html.find_all('b', text=re.compile('Exam Information'))
        if len(exam_info) > 0:
            exam_info = exam_info[0].parent
            if "Please contact" not in exam_info.text:
                for key, val in pairwise(exam_info.find_all('td')):
                    course_data[key.text] = val.text
            else:
                # Odd case where only the Exam Group is present
                course_data['Exam Group'] = exam_info.find('td').text.split(":")[1].strip()

        #print(exam_info.find_all('td')[1].text)
        #course_data['exam_date'] = exam_info.find_all('td')[2].text
        #print(exam_info.find_all('td')[3].text)
        #course_data['exam_time'] = exam_info.find_all('td')[3].text
        #course_data['exam_group'] = exam_info.find_all('td')[5].text

        # I thought there was exam location data? I can't seem to find it.
        # course_data['exam_building'] =
        # course_data['exam_room'] =

        course_data['critical_review'] = course_html\
            .find_all('a', text="Critical Review")[0]['href']

        '''
        TODO: course_data['books'] = []
        '''

        return course_data

    def __init__(self, username, password):
        self.s = None
        self.username = username
        self.password = password

    def __enter__(self):
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
        self.s.post(login_url, data=payload, headers=headers,
                    allow_redirects=True)

        return self

    def __exit__(self, ex_type, ex_value, traceback):
        return True  # Should probably handle exceptions here


def main():
    '''
    Main Function
    '''

    # Load up the username and password
    username = secret.username
    passwd = secret.password

    with SelfserviceSession(username, passwd) as s:
        for semester in SelfserviceSession.Semesters:
            # for department in SelfserviceSession.Departments:
            for department in ['CSCI']:
                for course in s.gen_courses(semester, department):
                    pprint({k: course[k] for k in course.keys() if "prerequisites" in k})

    '''
    def meta_redirect(content):
        soup = BeautifulSoup(content)
        result=soup.find("meta",attrs={"http-equiv":"refresh"})
        if result:
            wait,text=result["content"].split(";")
            if text.lower().startswith("url="):
                url=text[4:]
                return url
                return None
                while meta_redirect(p.content):
                    p = s.get('https://selfservice.brown.edu' +
                    meta_redirect(p.content))
    '''

main()
