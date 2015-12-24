import requests


def get_html(url, need_auth=False):
    ''' Returns the HTML data at a given URL as a string. '''
    cookies = {}
    if need_auth:
        ''' LaundryView is weird. It requires that we visit some pages in the
            same session that we visit the short URL *and* lvs.php. The request
            library loses cookies on redirect, so we have to
            visit the short URL first without redirects. '''
        r = requests.get("http://laundryview.com/brownu",
                         allow_redirects=False)
        cookies = r.cookies
        r = requests.get('http://laundryview.com/lvs.php?s=1921',
                         cookies=cookies)
        print(r.cookies)
    return requests.get(url, cookies=cookies).text
