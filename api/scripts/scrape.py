from eateries import Ratty

eatery_list = [Ratty()]

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
