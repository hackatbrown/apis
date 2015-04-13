from sys import argv
import time

from eateries import Ratty, VDub
from email_handler import send_alert_email

# as you add eateries, simply instantiate their class in this list for them to be scraped.
full_eatery_list = [VDub(), Ratty()]


##########################################################################

def scrape(eateries, get_menus=True, get_hours=True):
    total_menus, total_hours, total_time = 0, 0, 0
    for eatery in eateries:
        print
        print "Scraping data for:", eatery.name
        start = time.time()
        try:
            num_menus, num_hours = eatery.scrape(get_menus, get_hours)
        except:
            print "Could not scrape data for", eatery.name
            send_alert_email("Could not scrape data for " + eatery.name, urgent=True)
            continue
        elapsed = time.time() - start
        print num_menus, "menus and", num_hours, "hours scraped for", eatery.name, "in", str(elapsed), "seconds."
        total_menus += num_menus
        total_hours += num_hours
        total_time += elapsed
    print
    print total_menus, "total menus and", total_hours, "total hours scraped in", total_time, "seconds."

##########################################################################

if __name__ == '__main__':
    get_menus, get_hours = False, False
    eateries = []
    if len(argv) > 1:
        for arg in argv:
            if arg == '--hours' or arg == '-h':
                get_hours = True
            if arg == '--menus' or arg == '-m':
                get_menus = True
            if arg == '--ratty' or arg == '-r':
                eateries.append(Ratty())
            if arg == '--vdub' or arg == '-v':
                eateries.append(VDub())

    # if neither menus nor hours specified, scrape both
    if not get_menus and not get_hours:
        get_menus, get_hours = True, True

    # if no eateries specified, scrape all eateries
    if len(eateries) == 0:
        eateries = [Ratty(), VDub()]

    print "Scraping Brown Dining Services' sites for menus and hours..."
    scrape(eateries, get_menus, get_hours)
    print "Done scraping."
