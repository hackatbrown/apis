# vim: set ts=4 sts=4 sw=4 expandtab:
import re
from api.scripts.laundry import util, Machine

_room_static_url = "http://laundryview.com/staticRoomData.php?location=%s"
_room_dynamic_url = "http://laundryview.com/dynamicRoomData.php?location=%s"
_machine_id_re = re.compile(r'machine(Status|Data)([0-9]+)')


def to_str(room):
    return room['name'] + ' (' + room['id'] + ')'


def scrape_machines(room):
    html = util.get_html(_room_static_url % room['id'])
    machines = {}
    for kv in html.split('&'):
        if kv == '':
            continue

        (k, v) = kv.strip().split('=')

        if _machine_id_re.match(k) is not None:
            mid = _machine_id_re.match(k).group(2)
            machines[mid] = Machine.props_to_doc(mid, v)

    room['machines'] = list(machines.values())
    return room
