from api import db

from datetime import date

# simplify collection name
clients = db.clients

endpoints = set()


def get_request_stats():
    all_clients = clients.find()
    request_stats = {}
    for c in all_clients:
        client = {}
        client['client_email'] = c['client_email']
        client['count'] = c.get('requests', 0)
        for request in c.get('activity', []):
            endpoints.add(request['endpoint'])
            if request['endpoint'] in client:
                client[request['endpoint']] += 1
            else:
                client[request['endpoint']] = 1
        request_stats[c['username']] = client
    return request_stats


def get_total_requests():
    stats = get_request_stats()
    client_count = {c: 0 for c in stats.keys()}
    for client in stats.keys():
        req = stats[client].get('count', 0)
        client_count[client] += req
    return sum(client_count.values())


if __name__ == '__main__':
    stats = get_request_stats()
    client_count = {c: 0 for c in stats.keys()}
    for client in stats.keys():
        req = stats[client].get('count', 0)
        client_count[client] += req
    total_requests = sum(client_count.values())

    endpoint_count = {e: 0 for e in endpoints}
    for endpoint in endpoints:
        for client in stats.keys():
            req = stats[client].get(endpoint, 0)
            endpoint_count[endpoint] += req

    print("REQUEST STATISTICS AS OF", '{dt:%A}, {dt:%B} {dt.day}, {dt.year}'.format(dt=date.today()).upper())
    print()
    print("BY CLIENT:")
    for client in stats.keys():
        print('{0:<25} {1:>6}'.format(client, client_count[client]))

    print()
    print("BY ENDPOINT:")
    for endpoint in endpoints:
        print('{0:<25} {1:>6}'.format(endpoint, endpoint_count[endpoint]))

    print()
    print("TOTAL REQUESTS:", total_requests)
