# vim: set ts=4 sts=4 sw=4 expandtab:
import re
from bs4 import BeautifulSoup as soup

from api.scripts.laundry import Room, util

_campus_url = "http://laundryview.com/lvs.php"
_rid_re = re.compile(r".*\.php\?lr=([0-9]+)")


def scrape_rooms(collection):
    ''' collection is a pymongo collection object '''
    html = util.get_html(_campus_url)
    parsed = soup(html, 'html5lib')
    room_list = parsed.find('div', {'id': 'campus1'})
    links = room_list.find_all('a')
    rooms = []
    for link in links:
        rid = _rid_re.match(link['href']).group(1)
        name = link.text.strip()

        room = {'name': name, 'id': rid}
        existing_room = collection.find(room)

        if existing_room.count() == 0:
            room = Room.scrape_machines(room)
        else:
            room['machines'] = existing_room[0]['machines']

        rooms.append(room)
    return rooms
