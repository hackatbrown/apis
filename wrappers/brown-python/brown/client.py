import requests
import json
import collections

class Client:
    ''' A client for interacting with Brown resources '''

    use_ssl = True
    host = "brown-apis.herokuapp.com"

    def __init__(self, **kwargs):
        ''' Create a client instance with the provided options. Options should
            be passed in as kwargs.
        '''

        self.use_ssl = kwargs.get('use_ssl', self.use_ssl)
        self.host = kwargs.get('host', self.host)
        self.scheme = self.use_ssl and 'https://' or 'http://'
        self.options = kwargs

        self.client_id = kwargs.get('client_id')

        if 'client_id' not in kwargs:
            raise TypeError("A client_id must be provided.")

    def get(self, endpoint, **kwargs):
        ''' get a resource from a given endpoint with parameters in kwargs '''

        # attempt to correct common endpoint mistakes
        if endpoint[0] != '/':
            endpoint = '/' + endpoint
        if endpoint[-1] == '/':
            endpoint = endpoint[:-1]

        options = {'client_id': self.client_id}
        options.update(kwargs)

        url = self.scheme + self.host + endpoint

        return convert(json.loads(requests.get(url, params=options, verify=True).text))

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

if __name__ == '__main__':
    c = Client(client_id='test_client')
    while True:
        endpoint = raw_input("Endpoint: ")
        if endpoint == 'exit':
            break
        eatery = raw_input("Eatery: ")
        print c.get(endpoint, eatery=eatery)



