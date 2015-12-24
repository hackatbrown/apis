import urllib3


def get_html(url):
    ''' Returns the HTML data at a given URL as a string. '''
    data = urllib3.PoolManager().request('GET', url).data
    return data.decode()
