import unittest
import requests
import sys

base = "http://localhost:5000/academic"


class TestNonConflictingEndpoint(unittest.TestCase):

    def test_non_conflicting(self):
        # Test for time collisions
        mycourse = 'CSCI1670-S01'
        r = requests.get(base+"/courses/"+mycourse)
        data = r.json()
        mymeetings = data['meeting']

        def check_course(course):
            '''
            True - if clear
            False - if collision
            '''
            for m1 in mymeetings:
                for m2 in course['meeting']:
                    if m1['day_of_week'] == m2['day_of_week'] and\
                       m1['start_time'] <= m2['end_time'] and\
                       m1['end_time'] >= m2['start_time']:
                        print(m1)
                        print(m2)
                        return False
            return True

        r = requests.get(base+"/non-conflicting", params={'numbers': mycourse})
        data = r.json()
        while True:
            check_items(self, check_course, data['items'])
            if data['next'] == "null":
                break
            data = requests.get(data['next']).json()


class TestPagination(unittest.TestCase):

    def test_limit_constraint(self):
        ''' Makes sure we don't go over limit '''
        value = 4
        r = requests.get(base+"/departments/CSCI", params={"limit": value})
        data = r.json()
        while True:
            self.assertTrue(data['limit'] == value)
            self.assertTrue(len(data['items']) <= value)
            if data['next'] == "null":
                break
            data = requests.get(data['next']).json()

    def test_item_uniqueness(self):
        '''
        Run through all items and make sure we don't have duplicates
        '''
        count = 0
        seen = set()
        r = requests.get(base+"/courses")
        data = r.json()
        while True:
            count += len(data['items'])
            seen.update(set([i['_id']['$oid'] for i in data['items']]))
            if data['next'] == "null":
                break
            data = requests.get(data['next']).json()
        self.assertTrue(count == len(seen))

    def test_nothing_is_dropped(self):
        '''
        Test with different limits and see that you get the same number
        of items
        '''
        pass


def check_items(t, f, items):
    for item in items:
        t.assertTrue(f(item))

if __name__ == '__main__':
    unittest.main()
