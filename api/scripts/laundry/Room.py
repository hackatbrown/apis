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


def get_machine_statuses(room):
    html = util.get_html(_room_dynamic_url % room['id'], need_auth=True)[1:]
    for kv in re.split('\n&', html):
        if kv == '':
            continue

        (k, v) = kv.strip().split('=')
        if _machine_id_re.match(k) is not None:
            mid = _machine_id_re.match(k).group(2)
            # lol O(mn)
            for idx, mach in enumerate(room['machines']):
                if mach['id'] == mid:
                    props = v.split(':')
                    if props[6] == '0' or props[6] == '':
                        room['machines'][idx]['message'] = None
                    else:
                        room['machines'][idx]['message'] = props[6]
                    room['machines'][idx]['avail'] = bool(props[0])
                    room['machines'][idx]['time_remaining'] = int(props[1])
                    break
    return room
