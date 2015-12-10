import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup as soup
from datetime import date, timedelta
import time
from api import db

# simplify database names
menus = db.dining_menus
hours = db.dining_hours
all_foods = db.dining_all_foods

class Eatery:

    # a set of meal names to ignore, because dining services will often put items that aren't meals in the spreadsheets
    food_ignore_list = set(["closed for breakfast",
                            "closed for breakfat",
                            "closed for service",
                            "opens at lunch",
                            "winter 6",
                            "winter 7",
                            "winter 8",
                            "winter 9",
                            "winter 10",
                            "winter 11",
                            "winter 12",
                            "winter 13",
                            "spring 5",
                            "spring 6",
                            "spring 7",
                            "spring 8",
                            "spring 9",
                            "spring 10",
                            "spring 11",
                            "spring 12",
                            "for your safety, it is the customers obligation to inform the server about any food allergies.",
                            "for your safety, it is the customer's obligation to inform the server about any food allergies",
                            "",
                            ".",
                            "Look for Monthly Specials!"])
    base_url = "https://www.brown.edu/Student_Services/Food_Services/eateries/"

    def scrape(self, get_menus=True, get_hours=True):
        ''' This method is called on each eatery by ' r.py'
            Scrape menus and hours for this eatery and add them to database
            Return number of menus and hours scraped
        '''
        num_menus, num_hours = 0, 0
        if get_menus:
            num_menus = self.scrape_menus()
        if get_hours:
            num_hours = self.scrape_hours()
        return num_menus, num_hours

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

            Precondition: Day must be available as defined by find_available_days_and_meals
        '''
        pass

    def scrape_menus(self):
        ''' Scrape all available menus for this eatery
            Return number of menus added, add all menus to database
        '''
        pass

    def add_menu_to_db(self, year, month, day, meal, food, section_dict={}):
        ''' Add a single menu to the database
            Return True if successful, otherwise False
        '''
        # create separate menu docs to query and update the DB
        menu_query = {'eatery': self.name, 
                      'year': year,
                      'month': month,
                      'day': day,
                      'start_hour': self.mealtimes[meal]['start']['hour'],        
                      'start_minute': self.mealtimes[meal]['start']['minute'],     
                      'end_hour': self.mealtimes[meal]['end']['hour'], 
                      'end_minute': self.mealtimes[meal]['end']['minute'],
                      'meal': meal
                     }
        menu_full = {'food': food}
        menu_full.update(section_dict)
        menu_full.update(menu_query)
        return True if menus.update(menu_query, menu_full, upsert=True) else False

    def update_all_foods_in_db(self, food):
        ''' Update the eatery's food list in the all_foods collection
            Return True if successful, otherwise False
        '''
        return True if all_foods.update({'eatery':self.name}, {'$addToSet' : {'food': {'$each': food}}}, upsert=True) else False

    def scrape_hours(self):
        ''' Scrape hours for this eatery
            Return number of hours added, add hours to database
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
        return True if hours.update(hours_doc, hours_doc, upsert=True) else False



class Ratty(Eatery):

    def __init__(self):
        self.name = 'ratty'
        self.eatery_page = "refectory.php"
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
        ''' see description in superclass (Eatery) '''
        html = get_html(self.base_url + self.eatery_page)
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

    def scrape_menus(self):
        ''' see description in superclass (Eatery) '''
        ordered_days, days_meals = self.find_available_days_and_meals()
        menu_date = date.today()

        num_menus = 0

        error_did_occur = False

        if ordered_days and days_meals:
            for day in ordered_days:
                for meal in days_meals[day]:
                    import time
                    time.sleep(1) # delays for 1 second (BDS rate limits their site)
                    try:
                        print(meal, "for", day, menu_date, "->", self.scrape_menu(menu_date, day, meal))
                        num_menus += 1
                    except:
                        error_did_occur = True
                        import traceback
                        traceback.print_exc()
                        print("Could not scrape data for", meal, "on", day, menu_date)
                        print("Attempting to continue...")
                menu_date += timedelta(1)
        if error_did_occur:
            raise RuntimeError("Could not scrape data for at least one VDub meal.")
        return num_menus

    def scrape_menu(self, menu_date, day, meal):
        ''' see description in superclass (Eatery) '''
        # start at the main page for the Ratty
        main_html = get_html(self.base_url + self.eatery_page)
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
        if table == None:
            table = meal_parsed.find('table', {'class':'waffle'})
        rows = table.find_all('tr')[1:]
        cols = [unquote(col.text).lower() for col in rows[0].find_all('td')]
        data = {col:[] for col in cols}
        for row in rows[1:-1]:
            row_cols = row.find_all('td')
            for ix, c in enumerate(row_cols):
                if c.text and not c.text.lower().strip() in self.food_ignore_list:
                        data[cols[ix]].append(c.text.lower().strip())
        data['daily sidebars'] = [col.text.lower().strip() for col in rows[-1].findAll('td') \
                        if col.text and col.text.lower().strip() not in self.food_ignore_list]

        # For now, convert the dict into a single list of food items before adding to the DB
        flat_data = [d for d in flatten(data) if not d in self.food_ignore_list]
        return self.add_menu_to_db(menu_date.year, menu_date.month, menu_date.day, meal, flat_data, data) and \
               self.update_all_foods_in_db(flat_data)

    def scrape_hours(self):
        ''' see description in superclass (Eatery) '''
        # this hours scraper is only valid for Spring 2015
        num_hours = 0

        today = date.today()
        if today > date(2015, 12, 22):
            print("ERROR: hours scraper is out of date")
            return num_hours
        while today < date(2015, 12, 22):
            if today.month == 11 and today.day == 6:
                # Thanksgiving (open 11:30AM-7:30PM)
                num_hours += 1
                print("hours for {0}/{1}/{2} ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (11, 30), (19, 30)))
            elif today.month == 11 and today.day >= 27 and today.day <= 29:
                # Thanksgiving weekend (10:30AM-7:30AM)
                num_hours += 1
                print("hours for {0}/{1}/{2} ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (10, 30), (19, 30)))
            elif today.month == 12 and today.day == 20:
                # Finals period Sunday schedule (Weekday hours)
                num_hours += 1
                print("hours for {0}/{1}/{2} ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (7, 30), (19, 30)))
            elif today.weekday() == 6:
                # Sunday brunch schedule
                num_hours += 1
                print("hours for {0}/{1}/{2} ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (10, 30), (19, 30)))
            elif today.weekday() != 6:
                # weekday and Saturday schedule
                num_hours += 1
                print("hours for {0}/{1}/{2} ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (7, 30), (19, 30)))
            today = today + timedelta(1)
        return num_hours


class VDub(Eatery):

    def __init__(self):
        self.name = 'vdub'
        self.eatery_page = "verneywoolley_menu.php"
        self.mealtimes = {'breakfast':              {'start': {'hour':7, 'minute':30},
                                                       'end': {'hour':9, 'minute':30}},
                          'continental breakfast':  {'start': {'hour':9, 'minute':30},
                                                       'end': {'hour':11, 'minute':00}},
                          'lunch':                  {'start': {'hour':11, 'minute':00},
                                                       'end': {'hour':14, 'minute':00}},
                          'dinner':                 {'start': {'hour':16, 'minute':30},
                                                       'end': {'hour':19, 'minute':30}}
                         }

    def find_available_days_and_meals(self):
        ''' see description in superclass (Eatery) '''
        html = get_html(self.base_url + self.eatery_page)
        parsed_html = soup(html, 'html5lib')
        
        # search for all 'h4' tags on the page -- the VDub staff uses these as headers for the days available
        available_days = [h4.text.split()[0].lower() for h4 in parsed_html.find_all("h4")]
        
        # the VDub serves breakfast, continental breakfast, lunch, and dinner every weekday
        days_meals = {}
        for day in available_days:
            days_meals[day] = ['breakfast', 'continental breakfast', 'lunch', 'dinner']
        return (available_days, days_meals)

    def scrape_menus(self):
        ''' see description in superclass (Eatery) '''
        ordered_days, days_meals = self.find_available_days_and_meals()
        today = date.today()
        if today.weekday() == 6:
            menu_date = today + timedelta(1)
        elif today.weekday() == 5:
            menu_date = today + timedelta(2)
        else:
            menu_date = today

        num_menus = 0
        error_did_occur = False
        if ordered_days and days_meals:
            for n, day in enumerate(ordered_days):
                # menu_ids is a list [('breakfast', _id), ('continental breakfast', _id), ...]
                import time
                time.sleep(1) # delays for 1 second (BDS rate limits their site)
                try:
                    menu_ids = self.scrape_menu(menu_date, day, days_meals[day], n)
                    for menu_id in menu_ids:
                        print(menu_id[0], "for", day, menu_date, "->", menu_id[1])
                        num_menus += 1
                    menu_date += timedelta(1)
                except:
                    error_did_occur = True
                    import traceback
                    traceback.print_exc()
                    print("Could not scrape data for", menu_id[0], "on", day, menu_date)
                    print("Attempting to continue...")
        if error_did_occur:
            raise RuntimeError("Could not scrape data for at least one VDub meal.")
        return num_menus

    def scrape_menu(self, menu_date, day, meals, nth_day):
        ''' see description in superclass (Eatery) 
            nth_day - allows scraper to determine which table to use on VDub website
        '''
        # start at the main page for the VDub 
        main_html = get_html(self.base_url + self.eatery_page)
        main_parsed = soup(main_html, 'html5lib')  # the VDub website has errors, so the default parser fails -> use html5lib instead

        # get the nth_day's iframe
        iframes = main_parsed.find_all('iframe')
        nth_day_iframe = iframes[nth_day]

        # load the iframe's HTML content
        menu_html = get_html(nth_day_iframe['src'])
        meal_parsed = soup(menu_html, 'html5lib')

        # scrape the table into a dict of sections (Chef's Corner, Bistro, etc)
        table = meal_parsed.find('table', {'id':'tblMain'})
        if table == None:
            table = meal_parsed.find('table', {'class':'waffle'})
        rows = table.find_all('tr')[1:]
        cols = [unquote(col.text).lower() for col in rows[0].find_all('td')]
        data = {col:[] for col in cols}
        for row in rows[1:-1]:
            row_cols = row.find_all('td')
            for ix, c in enumerate(row_cols):
                if c.text:
                    data[cols[ix]].append(c.text.lower().strip())
        
        # continental breakfast doesn't have its own menu -- copy breakfast data
        data['continental breakfast'] = data['breakfast']

        results = []

        # add each meal's menu to DB
        for meal in meals:
            section_dict = {}
            section_dict['main menu'] = [d for d in data[meal] if not d in self.food_ignore_list]
            section_dict['daily sidebars'] = [d for d in data['daily sidebars'] if not d in self.food_ignore_list]
            flat_data = list({d.lower().strip() for d in data[meal] if not d in self.food_ignore_list for ds in data['daily sidebars'] \
                         if not ds in self.food_ignore_list})
            res_add = self.add_menu_to_db(menu_date.year, menu_date.month, menu_date.day, meal, flat_data, section_dict)
            res_update = self.update_all_foods_in_db(flat_data)
            results.append((meal, res_add and res_update))

        return results


    def scrape_hours(self):
        ''' see description in superclass (Eatery) '''
        # this scraper is only valid through Spring 2015
        num_hours = 0

        today = date.today()
        if today > date(2015, 12, 22):
            print("ERROR: hours scraper is out of date")
            return num_hours
        while today < date(2015, 12, 22):
            if today.month == 10 and today.day >= 10 and today.day <= 11:
                # fall break schedule
                pass
            elif today.month == 10 and today.day >= 17 and today.day <= 18:
                # parent's weekend schedule
                pass
            elif today.month == 11 and today.day == 25:
                # wednesday before thxgiving
                num_hours += 1
                print("hours for {0}/{1}/{2} (breakfast/lunch) ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (7, 30), (14, 00)))
            elif today.month == 11 and today.day >= 26 and today.day <= 29:
                # thxgiving weekend
                pass
            elif today.month == 12 and today.day >= 19 and today.day <= 20:
                # end of finals
                pass
            elif today.month == 12 and today.day == 21:
                # last day of finals
                num_hours += 1
                print("hours for {0}/{1}/{2} (breakfast/lunch) ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (7, 30), (14, 00)))
            elif today.weekday() >= 5:
                # weekend schedule
                pass
            elif today.weekday() <= 4:
                # weekday schedule
                num_hours += 2
                print("hours for {0}/{1}/{2} (breakfast/lunch) ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (7, 30), (14, 00)))
                print("hours for {0}/{1}/{2} (dinner) ->".format(today.month, today.day, today.year), self.add_hours_to_db(today.year, today.month, today.day, (16, 30), (19, 30)))
            today = today + timedelta(1)

        return num_hours



class Jos(Eatery):

    def __init__(self):
        self.name = "jos"
        self.eatery_page = "josiahs.php"
        self.mealtimes = {'dinner':   {'start': {'hour':18, 'minute':00},
                                       'end': {'hour':26, 'minute':00}}}

    def find_available_days_and_meals(self):
        return None

    def scrape_menu(self, menu_date, day, meal):
        return None

    def scrape_hours(self):
        #TODO: Implement Jos scraping
        return None

######### IvyRoom PROJECT ##########

#Weekday Lunch
# 11:30am - 1:45pm
# Night
# 7:45pm - Midnight (Sun-Thu)
class IvyRoom(Eatery):
    '''Author: kcockrel'''
    def __init__(self):
        self.name = "ivyroom"
        self.eatery_page = "ivyroom_menu.php"
        self.regular_page = "ivyroom.php"
        self.mealtimes = {' lunch':  {'start': {'hour':11, 'minute':30}, 
                                    'end': {'hour':13, 'minute': 45}},
                            'dinner':   {'start': {'hour': 19, 'minute': 45},
                                    'end': {'hour': 24, 'minute': 00}}}

    def find_available_days_and_meals(self):
        ''' see description in superclass (Eatery) '''

        html = get_html(self.base_url + self.eatery_page)
        parsed_html = soup(html, 'html5lib')
        
        # search for all 'h4' tags on the page -- the IvyRoom staff uses these as headers for the days available
        available_days = [h4.text.split()[0].lower() for h4 in parsed_html.find_all("h4")]
    
        # the IvyRoom is open for lunch on weekdays & open nights Sun-Thurs
        days_meals = {}
        for day in available_days:
            if day != 'friday':
                days_meals[day] = ['lunch', 'dinner']
            else:
                days_meals[day] = ['lunch']

        return (available_days, days_meals)
    
    def scrape_menus(self):
        ''' see description in superclass (Eatery) '''
        # the IvyRoom is open for lunch on weekdays & open nights Sun-Thurs

        ordered_days, days_meals = self.find_available_days_and_meals()
        today = date.today()
        #IvyRoom is closed on Saturdays
        if today.weekday() == 5:
            menu_date = today + timedelta(1)
        else:
            menu_date = today

        #TODO: Add menus to the database. Talk to Joe about how they should be added. 
        #(Ratty & VDub are done differently)

       
        return None

    def scrape_menu(self, menu_date, day, meals, nth_day):
        ''' see description in superclass (Eatery) 
            nth_day - allows scraper to determine which table to use on VDub website
            NOTE: Only the lunch menu is shown on the table
            Dinner menu must be scraped from ivyroom.php 
        '''

        # start at the menu page for the IvyRoom
        #Note that this page only contains the changing menu items @ the IR
        #There are some things they serve regularly on the regular page
        main_html = get_html(self.base_url + self.eatery_page)
        main_parsed = soup(main_html, 'html5lib')  # the website has errors, so the default parser fails -> use html5lib instead

        # get the nth_day's iframe
        iframes = main_parsed.find_all('iframe')
        nth_day_iframe = iframes[nth_day]

        # load the iframe's HTML content
        menu_html = get_html(nth_day_iframe['src'])
        meal_parsed = soup(menu_html, 'html5lib')

        table = meal_parsed.find('table', {'id':'tblMain'})
        if table == None:
            table = meal_parsed.find('table', {'class':'waffle'})

        #Lunch is a list of the changing lunch menu items
        lunch = []

        rows = table.findChildren('tr')
        for row in rows:
            cols = row.findChildren('td')
            for col in cols:
                value = col.string
                if value != None:
                    lunch.append(value)
        
        ''' Pulling menu items from ivyroom.php,, ie, the page with the recurring food menu items
        '''
        main_html = get_html(self.base_url + self.regular_page)
        main_parsed = soup(main_html, 'html5lib') 
        
        uls = main_parsed.find_all('ul', {'class':'lcol'})
        dinner = []

        #TODO: Add things to food ignore list
        
        lunch_regulars = uls[0]
        dinner_regulars = uls[1]

        #TODO: Update this so that it pulls all lunch list items for lunch, not just strong

        lunch_list = lunch_regulars.findChildren('strong')
        for i in lunch_list:
            value = i.string
            if value not in self.food_ignore_list:
                lunch.append(value)

        dinner_list = dinner_regulars.findChildren('strong')

        for i in dinner_list:
            value = i.string
            if value not in self.food_ignore_list:
                dinner.append(value)

        print("DINNER:")
        print(dinner)
        print("LUNCH")
        print(lunch)
        #find the 

        #TODO: Add the menu items to the database
        results = []

        return None

    def scrape_hours(self):
        ''' Scrape hours for this eatery
            Return number of hours added, add hours to database
        '''
        #TODO
        num_hours = 0
        today = date.today()

        if today > date(2015, 12, 22):
            print("ERROR: hours scraper is out of date")
            return num_hours

        while today < date(2015, 12, 22):

            #If it's thanksgiving weekend, IR is closed
            if today.month == 11 and today.day >=26 and today.day <= 29:
                pass
            elif today.weekday() == 4 or today.weekday() == 5 :
                #TODO: Fix this. IvyRoom IS open for lunch on Fridays
                #weekend schedule
                #IR is closed sat
                pass
            elif today.weekday() == 6:
                #dinner on sunday, no lunch

                num_hours += 1
                print("hours for {0}/{1}/{2} (dinner) -> ".format(today.month, today.day, today.year), 
                    self.add_hours_to_db(today.year, today.month, today.day, (19,45), (24, 00)))

            elif today.weekday() <= 3:
                #weekday schedule
                #sun - thurs
                num_hours += 2

                print("hours for {0}/{1}/{2} (lunch) ->".format(today.month, today.day, today.year), 
                    self.add_hours_to_db(today.year, today.month, today.day,(11,30),(13,45)))
                print("hours for {0}/{1}/{2} (dinner) ->".format(today.month, today.day, today.year), 
                    self.add_hours_to_db(today.year, today.month, today.day,(19,45), (24,00)))
            today = today + timedelta(1)

        return num_hours

# Helper methods

def get_html(url):
    ''' The HTML data for a given URL '''
    return requests.get(url).text

def flatten(dct):
    ''' Flatten a dictionary's values into a list '''
    result = []
    for val in dct.values():
        result += val
    return list(set(result))


