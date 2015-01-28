from urllib2 import Request, unquote, urlopen
from bs4 import BeautifulSoup as soup
from datetime import date, timedelta
from api import db

# simplify database names
menus = db.dining_menus
hours = db.dining_hours

class Eatery:

    def scrape(self):
        ''' This method is called on each eatery by 'scraper.py'
            Return None, scrape menus and hours for this eatery and add them to database
        '''
        self.scrape_menus()
        self.scrape_hours()

    def find_available_days_and_meals(self):
        ''' Find the days and meals for which menus are available
            Return a tuple of the week days available (in order of date) and
                 a dict of those days mapped to lists of meals
                 ex: (['saturday', 'sunday', 'monday'],
                      {'saturday':['breakfast', 'lunch', 'dinner'],
                       'sunday':['lunch', 'dinner'],
                       'monday':['breakfast', 'lunch', 'dinner']}])
        '''
        pass

    def scrape_menu(self, menu_date, day, meal):
        ''' Scrape a single menu for a given day and meal (menu_date is provided because
            it is a field in the menu's database document)
            Return None, just add menu to database (db.dining_menus)
        '''
        pass

    def scrape_menus(self):
        ''' Scrape all available menus for this eatery
            Return None, add all menus to database
        '''
        ordered_days, days_meals = self.find_available_days_and_meals()
        menu_date = date.today()

        for day in ordered_days:
            for meal in days_meals[day]:
                print meal, "for", day, menu_date, "->", self.scrape_menu(menu_date, day, meal)
            menu_date += timedelta(1)

    def add_menu_to_db(self, year, month, day, meal, food):
        ''' Add a single menu to the database
            Return the ObjectID of the menu in the database
        '''
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

    def scrape_hours(self):
        ''' Scrape hours for this eatery
            Return None, add hours to database
        '''
        pass

    def add_hours_to_db(self, year, month, day, open_time, close_time):
        ''' Add a single hours document to the database
            'open' and 'close' are tuples (<hour>, <minute>)
            Return the ObjectID of the hours document in the database
        '''
        hours_doc = {'eatery': self.name,
                     'year': year,
                     'month': month,
                     'day': day,
                     'open_hour': open_time[0],
                     'open_minute': open_time[1],
                     'close_hour': close_time[0],
                     'close_minute': close_time[1]
                    }
        return hours.update(hours_doc, hours_doc, upsert=True)['electionId']



class Ratty(Eatery):

    def __init__(self):
        self.name = 'ratty'
        self.base_url = "https://www.brown.edu/Student_Services/Food_Services/eateries/"
        self.home_ext = "refectory.php"
        self.mealtimes = {'breakfast': {'start': {'hour':7, 'minute':30},
                                          'end': {'hour':11, 'minute':00}},
                          'brunch':    {'start': {'hour':10, 'minute':30},
                                          'end': {'hour':16, 'minute':00}},
                          'lunch':     {'start': {'hour':11, 'minute':00},
                                          'end': {'hour':16, 'minute':00}},
                          'dinner':    {'start': {'hour':16, 'minute':00},
                                          'end': {'hour':19, 'minute':30}}
                         }

    def find_available_days_and_meals(self):
        html = get_html(self.base_url + self.home_ext)
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
        # start at the main page for the Ratty 
        main_html = get_html(self.base_url + self.home_ext)
        main_parsed = soup(main_html, 'html5lib')  # the Ratty website has errors, so the default parser fails -> use html5lib instead
        
        # Navigate to the specified day
        menus_url = main_parsed.find('table', {'class':'lines'}).find('a', text=day.title())['href']
        menus_html = get_html(self.base_url + menus_url)
        menus_parsed = soup(menus_html, 'html5lib')

        # Convert 'brunch' to 'lunch' in order to navigate the HTML correctly
        meal_query = 'lunch' if meal == 'brunch' else meal
        
        # Get the table for the specified meal
        meal_url = menus_parsed.find('iframe', {'id':meal_query.title()})['src']
        meal_html = get_html(meal_url)
        meal_parsed = soup(meal_html, 'html5lib')

        # Scrape the table into a dict of sections (Chef's Corner, Bistro, etc)
        table = meal_parsed.find('table', {'id':'tblMain'})
        rows = table.find_all('tr')[1:]
        cols = [unquote(col.text) for col in rows[0].find_all('td')[1:]]
        data = {col:[] for col in cols}
        for row in rows[1:-1]:
            row_cols = row.find_all('td')[1:]
            for ix, c in enumerate(row_cols):
                if c.text:
                    data[cols[ix]].append(c.text)
        data['Other'] = [col.text for col in rows[-1].findAll('td') if col.text and col.text != '.']

        # For now, convert the dict into a single list of food items before adding to the DB
        data = [d.lower() for d in flatten(data)]
        return self.add_menu_to_db(menu_date.year, menu_date.month, menu_date.day, meal, data)

    def scrape_hours(self):
        # this hours scraper is only valid for Spring 2015
        today = date.today()
        if today < date(2015, 5, 15):
            # only update once during the semester
            print "hours are up to date"
            return
        while (today.month != 5 or today.day != 16):
            if today.month == 3 and today.day >= 21 and today.day <= 28:
                # Spring break schedule
                pass
            elif today.weekday() == 6:
                # Sunday brunch schedule
                print "hours for {0}/{1}/{2} ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (10, 30), (19, 30))
            elif today.weekday() != 6:
                # Weekday and Saturday schedule
                print "hours for {0}/{1}/{2} ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (7, 30), (19, 30))
            today = today + timedelta(1)



class VDub(Eatery):

    def __init__(self):
        self.name = 'ratty'
        self.site_url = "http://www.brown.edu/Student_Services/Food_Services/eateries/verneywoolley_menu.php"
        self.menu_url_base = "https://docs.google.com/spreadsheet/pub?hl=en_US&hl=en_US&key=0Aui-7xDvNkAIdElldE13aXl4RlNZTmtjNzhhaDg1Q0E&gid=0&output=html&widget=false&range=%s:%s"
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
                                          'end': {'hour':16, 'minute':00}},
                          'lunch': {'start': {'hour':11, 'minute':00},
                                          'end': {'hour':16, 'minute':00}},
                          'dinner': {'start': {'hour':16, 'minute':00},
                                          'end': {'hour':19, 'minute':30}}
                         }

    def find_available_days_and_meals(self):
        return None

    def scrape_menu(self, menu_date, day, meal):
        #TODO: Implement VDub scraping
        return None

    def scrape_hours(self):
        #TODO: Implement VDub Hour Scraping
        return None



class Jos(Eatery):

    def __init__(self):
        #TODO: Setup Jos local variables
        pass

    def find_available_days_and_meals(self):
        #TODO: Implement Jos scraping
        return None

    def scrape_menu(self, menu_date, day, meal):
        #TODO: Implement Jos scraping
        return None

    def scrape_hours(self):
        #TODO: Implement Jos scraping
        return None



# Helper methods

def get_html(url):
    ''' The HTML data for a given URL '''
    return urlopen(Request(url)).read()

def flatten(dct):
    ''' Flatten a dictionary's values into a list '''
    result = []
    for val in dct.values():
        result += val
    return list(set(result))


