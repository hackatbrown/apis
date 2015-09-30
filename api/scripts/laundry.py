# vim: set ts=4 sts=4 sw=4 expandtab:
from urllib2 import Request, unquote, urlopen
from bs4 import BeautifulSoup as soup
from datetime import date, timedelta
import time
import re

campus_url="http://laundryview.com/lvs.php"
room_static_url="http://laundryview.com/staticRoomData.php?location=%s"
room_dynamic_url="http://laundryview.com/dynamicRoomData.php?location=%s"

machine_id_re = re.compile(r'machine(Status|Data)([0-9])+')

class MachineTypes:
    DRYER = 'dry'
    COMBO = 'washNdry'
    WASHER = 'washFL'

    @staticmethod
    def all():
        return [
            MachineTypes.DRYER,
            MachineTypes.COMBO,
            MachineTypes.WASHER
        ];

class Machine:
    def __init__(self, id, props):
        self.id = id
        props = props.split(':')
        self.type = props[3]
        self.time_remaining = 0

    def update_status(self, props):
        if self.type not in MachineTypes.all():
            return

        props = props.split(':')
        self.time_remaining = props[1]
        self.avail = props[0]
        self.message = None if props[6] == '0' else props[6]

        print self.avail, self.time_remaining, self.message

    def __str__(self):
        return self.type + ' #' + self.id

    __repr__ = __str__

class Room:
    def __init__(self, name, id):
        self.id = id
        self.name = name
        self.machines = None

    def __str__(self):
        return self.name + ' (' + self.id + ')'

    def scrape_machines(self):
        html = get_html(room_static_url % self.id)
        machines = {}
        for kv in html.split('&'):
            if kv == '':
                continue
            
            (k, v) = kv.strip().split('=')

            if machine_id_re.match(k) is not None:
                mid = machine_id_re.match(k).group(2)
                machines[mid] = Machine(mid, v)

        self.machines = machines

    def scrape_machine_statuses(self):
        if not self.machines:
            return
        html = get_html(room_dynamic_url % self.id)
        for kv in html.split('&'):
            if kv == '':
                continue

            (k, v) = kv.strip().split('=')
            
            match = machine_id_re.match(k)
            if match is not None:
                mid = match.group(2)
                self.machines[mid].update_status(v)

        print self.machines

    __repr__ = __str__

class Campus:
    def scrape(self):
        rid_re = re.compile(r".*\.php\?lr=([0-9]+)")
        html = get_html(campus_url)
        parsed = soup(html, 'html5lib')
        room_list = parsed.find('div', {'id': 'campus1'})
        links = room_list.find_all('a')
        rooms = []
        for link in links:
            rid = rid_re.match(link['href']).group(1)
            name = link.text.strip()
            rm = Room(name, rid)
            print name
            rm.scrape_machines()
            rm.scrape_machine_statuses()
            return 1
            rooms.append(Room(name, rid))

        print rooms

def get_html(url):
    ''' The HTML data for a given URL '''
    return urlopen(Request(url)).read()

c = Campus()
c.scrape()
