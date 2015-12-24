# vim: set ts=4 sts=4 sw=4 expandtab:


def props_to_doc(machine_id, prop_str):
    prop_list = prop_str.split(':')
    return {'type': prop_list[3], 'id': machine_id, 'message': None}


def update_status(machine_doc, prop_str):
    prop_list = prop_str.split(':')
    if prop_list[6] == '0':
        machine_doc['message'] = None
    else:
        machine_doc['message'] = prop_list[6]

    machine_doc['avail'] = prop_list[0]
    machine_doc['time_remaining'] = prop_list[1]

    return machine_doc


def to_str(doc):
    return doc['type'] + ' #' + doc['id']


types = {
    'dry': 'dryer',
    'washNdry': 'combo',
    'washFL': 'washer'
}
