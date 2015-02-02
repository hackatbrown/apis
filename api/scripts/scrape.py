from eateries import Ratty, VDub

#As you add eateries, simply instantiate their class in this list for them to be scraped.
eatery_list = [VDub()]


##########################################################################

def scrape():
    for eatery in eatery_list:
        eatery.scrape()

##########################################################################

if __name__ == '__main__':
    print "Scraping Brown Dining Services' sites for menus and hours..."
    scrape()
    print "Done scraping."
