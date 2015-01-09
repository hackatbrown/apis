from eateries import Ratty

eatery_list = [Ratty()]
daySeq = ['sunday', 'monday','tuesday','wednesday','thursday','friday','saturday']
mealSeq = ['breakfast','lunch','dinner']

def get_menu(eatery, day, meal):
    if eatery != 'ratty':
        return {}
    menu_range = day_ranges[day][meal]
    menu_url  = get_url(eatery, menu_range)
    menu_html = get_html(menu_url)
    menu_data = parse_menu(eatery, menu_html)
    return menu_data

def get_gen(eateries, days, meals):
    data = defaultdict(lambda : defaultdict(dict))
    for eatery in eateries:
        for day in days:
            for meal in meals:
                data[eatery][day][meal] = get_menu(eatery, day, meal)
        data[eatery] = dict(data[eatery])
    return dict(data)

##########################################################################

def scrape_all_hours():
    pass

def scrape_all_menus():
    for eatery in eatery_list:
        eatery.scrape()


##########################################################################

if __name__ == '__main__':
    print "Scraping Brown Dining Services' sites for menus and hours..."
    scrape_all_hours()
    scrape_all_menus()
    print "Done scraping."
