from eateries import Ratty

eatery_list = [Ratty()]

##########################################################################

def scrape():
    for eatery in eatery_list:
        eatery.scrape()

##########################################################################

if __name__ == '__main__':
    print "Scraping Brown Dining Services' sites for menus and hours..."
    scrape()
    print "Done scraping."
