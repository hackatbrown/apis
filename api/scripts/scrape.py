from sys import argv
import time

from eateries import Ratty, VDub

# as you add eateries, simply instantiate their class in this list for them to be scraped.
eatery_list = [VDub(), Ratty()]


##########################################################################

def scrape(get_menus=True, get_hours=True):
    total_menus, total_hours, total_time = 0, 0, 0
    for eatery in eatery_list:
        print
        print "Scraping data for: ", eatery.name
        start = time.time()
        num_menus, num_hours = eatery.scrape(get_menus, get_hours)
        elapsed = time.time() - start
        print num_menus, "menus and", num_hours, "hours scraped for", eatery.name, "in", str(elapsed), "seconds"
        total_menus += num_menus
        total_hours += num_hours
        total_time += elapsed
    print
    print total_menus, "total menus and", total_hours, "total hours scraped in", total_time, "seconds"

##########################################################################

if __name__ == '__main__':
    get_menus, get_hours = True, True
    if len(argv) > 1:
        for arg in argv:
            if arg == '--no-hours' or arg == '-h':
                get_hours = False
            if arg == '--no-menus' or arg == '-m':
                get_menus = False
    print "Scraping Brown Dining Services' sites for menus and hours..."
    scrape(get_menus, get_hours)
    print "Done scraping."
