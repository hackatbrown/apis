import requests


def get_html(url):
    ''' Returns the HTML data at a given URL as a string. '''
    return requests.get(url).text
