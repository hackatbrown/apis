from bs4 import BeautifulSoup
from copy import deepcopy
import requests
import logging
import re

'''
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

class SelfserviceSession():
    
    # Hard code these values. Bringing a full browswer into our stack to execute JS
    # for this is not worth. Possible TODO: Add some Date functionality to determine what
    # seasons/years to populate this list.
    #Semesters = ['Spring 2015', 'Summer 2015', 'Fall 2015', 'Spring 2016']
    Semesters = generate_semesters(3)
    Departments = ['AFRI','AMST','ANTH','APMA','ARAB','ARCH','ASYR','BEO','BIOL','CATL','CHEM','CHIN','CLAS','CLPS','COLT','CROL','CSCI','CZCH','DEVL','EAST','ECON','EDUC','EGYT','EINT','ENGL','ENGN','ENVS','ERLY','ETHN','FREN','GEOL','GNSS','GREK','GRMN','HIAA','HISP','HIST','HMAN','HNDI','INTL','ITAL','JAPN','JUDS','KREA','LAST','LATN','LING','LITR','MATH','MCM','MDVL','MED','MES','MGRK','MUSC','NEUR','PHIL','PHP','PHYS','PLCY','PLME','PLSH','POBS','POLS','PRSN','RELS','REMS','RUSS','SANS','SCSO','SIGN','SLAV','SOC','SWED','TAPS','TKSH','UNIV','URBN','VISA']
    
    # The standard headers for sending a request. Typically you'll add a Referer.
    BaseHeaders = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/43.0.2357.130 Chrome/43.0.2357.130 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Origin': 'https://selfservice.brown.edu'
    }

    def get_base_headers(self):
        return deepcopy(BaseHeaders)

    @staticmethod
    def _semester_to_value(semester_string):
        '''
        >>> [ __semester_to_value(s) for s in ['Spring 2015', 'Summer 2015', 'Fall 2015', 'Spring 2016']]
        [201420, 201500, 201510, 201520]
        '''
        words = semester_string.split(' ')
        assert(len(words) == 2)
        assert(int(words[1]) > 2010) #Not really needed.
        res = int(words[1]) * 100
        if words[0] == 'Fall':
            res += 10
        elif words[0] == 'Spring':
            res -= 100
            res += 20
        elif words[0] == 'Summer':
            pass
        else:
            print "ERROR: Unidentified Semester"
        return res

    @staticmethod
    def _value_to_semester(value):
        '''
        >>> [ __value_to_semester(v) for v in [201420, 201500, 201510, 201520]]
        ['Spring 2015', 'Summer 2015', 'Fall 2015', 'Spring 2016']
        '''
        year = int(value[:4]) #Get Year
        season = value[-2:]
        if season == "00":
            return str(year) + " Summer"
        elif season == "10":
            return str(year) + " Fall"
        elif season == "20":
            return str(year + 1) + " Spring"
        else:
            print "ERROR: Unidentified Semester"

    def gen_courses(self, semester, department):
        url = 'https://selfservice.brown.edu/ss/hwwkcsearch.P_Main'
        payload = {
            'IN_TERM': SelfserviceSession._semester_to_value(semester),
            'IN_SUBJ': department,
            'IN_SUBJ_multi':department,
            'IN_TITLE': '',
            'IN_INST': '',
            'IN_CRSE': '',
            'IN_ATTR': 'ALL',
            'IN_INDP': 'on',
            'IN_HOUR': '',
            'IN_DESCRIPTION': '',
            'IN_CREDIT': 'ALL',
            'IN_DEPT': 'ALL',
            'IN_METHOD':'S',
            'IN_CRN': '',
        }
        
        headers = get_base_headers()
        headers['Referer'] = url
        
        r = self.s.post(url, data=payload, headers=headers)

        # Jank extraction of args for Show_Details page
        for line in r.text.split("\n"):
            i = line.find('Show_Detail')
            #print line.find('n_term')
            if i != -1 and line.find('n_term') == -1:
                deets_args = line[i+13:i+34].split("','")
                print deets_args
                self._extract_course(deets_args)

        yield r #Does nothing atm

    def _extract_course(self,args):
        url = 'https://selfservice.brown.edu/ss/hwwkcsearch.P_Detail'
        payload = {
            'IN_TERM': args[0],
            'IN_CRN': args[1],
            'IN_FROM': '3',
        }

        headers = get_base_headers()
        headers['Referer'] = "https://selfservice.brown.edu/ss/hwwkcsearch.P_Main"
    
        r = self.s.post(url, data=payload, headers=headers)
        info = BeautifulSoup(r.content,'html.parser').select("#CourseDetailx")[0]
        print info
        if not info:
            exit(0)
        print info.get_text()
        return 
    
    def __init__(self, username, password):
        self.s = None
        self.username = username
        self.password = password

    def __enter__(self):
        url = "https://selfservice.brown.edu/ss/twbkwbis.P_GenMenu?name=bmenu.P_MainMnu"
        login_url = "https://selfservice.brown.edu/ss/twbkwbis.P_ValLogin"
        headers = get_base_headers()
        headers['Referer'] = url
        
        payload = {
            'sid': self.username,
            'PIN': self.password
        }
        self.s = requests.Session()
        p = self.s.get(url); #Get session id/cookies
        p = self.s.post(login_url, data=payload, headers=headers, allow_redirects=True)
        return self

    def __exit__(self, type, value, traceback):
        s = None
        return True # Should probably handle exceptions here

def gen_current_semester():
    '''
    Generates the semester string for the current semester.
    This uses fixed months for each semester, which isn't exactly optimal.
    
    I/P: Nothing.
    O/P: A valid semester string "(Fall/Summer/Spring) YEAR"
    '''
    seasons = [("Spring ",{1,2,3,4,5})  , ("Summer ", {6, 7}), ("Fall ", {8, 9, 10, 11, 12})]
    today = date.today()
    year = today.year
    month = today.month
    seasonTuple = filter(lambda (seas, dates): month in dates, seasons)[0][0]
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


def main():

    username = ''
    passwd = ''

    with SelfserviceSession(username,passwd) as s:
        for semester in SelfserviceSession.Semesters:
            print semester
            for department in SelfserviceSession.Departments:
                print department
                for course in s.gen_courses(semester, department):
                    print r
                    print "YAY"
                    exit(0);



    #def meta_redirect(content):
        #soup = BeautifulSoup(content)
        #result=soup.find("meta",attrs={"http-equiv":"refresh"})
        #if result:
            #wait,text=result["content"].split(";")
            #if text.lower().startswith("url="):
                #url=text[4:]
                #return url
        #return None
        #while meta_redirect(p.content):
            #p = s.get('https://selfservice.brown.edu' + meta_redirect(p.content))

main()
