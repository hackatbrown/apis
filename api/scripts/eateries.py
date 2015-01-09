from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from urllib2 import Request, unquote, urlopen
from bs4 import BeautifulSoup as soup
from datetime import date, timedelta
from api import db

# simplify database names
menus = db.dining_menus
hours = db.dining_hours

class Eatery:

    ''' 
    finds the days and meals for which menus are available
    returns: a tuple of the week days available (in order of date) and
             a dict of those days mapped to lists of meals
             ex: (['saturday', 'sunday', 'monday'],
                  {'saturday':['breakfast', 'lunch', 'dinner'],
                   'sunday':['lunch', 'dinner'],
                   'monday':['breakfast', 'lunch', 'dinner']}])
    '''
    def find_available_days_and_meals(self):
        pass

    def scrape_menu(self, menu_date, day, meal):
        pass

    def scrape(self):
        self.scrape_menus()
        self.scrape_hours()

    def scrape_menus(self):
        ordered_days, days_meals = self.find_available_days_and_meals()
        menu_date = date.today()

        for day in ordered_days:
            for meal in days_meals[day]:
                print meal, "for", day, menu_date, "->", self.scrape_menu(menu_date, day, meal)
            menu_date += timedelta(1)

    def scrape_hours(self):
        pass

class Ratty(Eatery):

    def __init__(self):
        self.name = 'ratty'
        self.site_url = "http://www.brown.edu/Student_Services/Food_Services/eateries/refectory_menu.php"
        self.menu_url_base = "https://docs.google.com/spreadsheet/pub?hl=en_US&hl=en_US&key=0AlK5raaYNAu5dE5GM0RoZ0lHSDdEUC1KdjZjZTZkekE&gid=0&output=html&widget=false&range=%s:%s"
        self.day_meal_ranges = {
                                'monday': {
                                                'breakfast':['R2C1','R14C4'],
                                                'lunch':['R2C5','R14C8'],
                                                'dinner':['R2C9', 'R14C12']
                                          },
                                'tuesday': {
                                                'breakfast':['R2C13','R14C16'],
                                                'lunch':['R2C17','R14C20'],
                                                'dinner':['R2C21', 'R14C24']
                                           },
                                'wednesday': {
                                                'breakfast':['R2C25','R14C28'],
                                                'lunch':['R2C29','R14C32'],
                                                'dinner':['R2C33', 'R14C36']
                                             },
                                'thursday': {
                                                'breakfast':['R2C37','R14C40'],
                                                'lunch':['R2C41','R14C44'],
                                                'dinner':['R2C45', 'R14C48']
                                            },
                                'friday': {
                                                'breakfast':['R2C49','R14C52'],
                                                'lunch':['R2C53','R14C56'],
                                                'dinner':['R2C57', 'R14C60']
                                          },
                                'saturday': {
                                                'breakfast':['R2C61','R14C64'],
                                                'lunch':['R2C65','R14C68'],
                                                'dinner':['R2C69', 'R14C72']
                                            },
                                'sunday': {
                                                'breakfast':['R2C73','R14C76'],
                                                'brunch':['R2C77','R14C80'],
                                                'lunch':['R2C77','R14C80'],
                                                'dinner':['R2C81', 'R14C84']
                                          }
                                }
        self.mealtimes = {'breakfast': {'start': {'hour':7, 'minute':30},
                                          'end': {'hour':11, 'minute':00}},
                          'brunch': {'start': {'hour':10, 'minute':30},
                                          'end': {'hour':4, 'minute':00}},
                          'lunch': {'start': {'hour':11, 'minute':00},
                                          'end': {'hour':4, 'minute':00}},
                          'dinner': {'start': {'hour':4, 'minute':00},
                                          'end': {'hour':7, 'minute':30}}
                         }

    def find_available_days_and_meals(self):
        html = get_html(self.site_url)
        parsed = soup(html, 'html5lib')
        table  = parsed.find('table', {'class':'lines'})
        rows = table.find_all('tr')[1:]
        days = [str(unquote(r.find_all('td')[1].text)).lower() for r in rows]
        days_meals = {}
        for day in days:
            if day != 'sunday':
                days_meals[day] = ['breakfast', 'lunch', 'dinner']
            else:
                days_meals[day] = ['brunch', 'dinner']
        return (days, days_meals)

    def scrape_menu(self, menu_date, day, meal):
        url = self.get_url(self.day_meal_ranges[day][meal])
        html = get_html(url)
        parsed = soup(html, 'html5lib')  # the Ratty website has errors, so the default parser fails -> use html5lib instead
        table  = parsed.find('table', {'id':'tblMain'})
        rows   = table.find_all('tr')[1:]
        cols = [unquote(col.text) for col in rows[0].find_all('td')[1:]]
        data = {col:[] for col in cols}
        for row in rows[1:-1]:
            row_cols = row.find_all('td')[1:]
            for ix, c in enumerate(row_cols):
                if c.text:
                    data[cols[ix]].append(c.text)
        data['Other'] = [col.text for col in rows[-1].findAll('td') if col.text and col.text != '.']
        data = [d.lower() for d in flatten(data)]
        return self.add_menu_to_db(menu_date.year, menu_date.month, menu_date.day, meal, data)

    def add_menu_to_db(self, year, month, day, meal, food):
        menu = {'eatery': self.name, 
                'year': year,
                'month': month,
                'day': day,
                'start_hour': self.mealtimes[meal]['start']['hour'],        
                'start_minute': self.mealtimes[meal]['start']['minute'],     
                'end_hour': self.mealtimes[meal]['end']['hour'], 
                'end_minute': self.mealtimes[meal]['end']['minute'],
                'food': food
               }
        return menus.update(menu, menu, upsert=True)['electionId']

    def get_url(self, meal_range):
        return self.menu_url_base % tuple(meal_range)

def get_html(url):
    return urlopen(Request(url)).read()

# utility method to flatten dictionaries
def flatten(dct):
    result = []
    for val in dct.values():
        result += val
    return list(set(result))


