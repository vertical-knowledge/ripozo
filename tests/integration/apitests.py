__author__ = 'Tim Martin'
import unittest
import json
import random
import logging
from datetime import datetime, timedelta
import string
from decimal import Decimal
from cqlengine.query import DoesNotExist
from tests.test_models import Person, Dummy
from tests.base import FakeAppBase

logger = logging.getLogger(__name__)


def create_request_parameters_from_dict(to_convert):
    l = []
    for key, value in to_convert:
        l.append('{0}={1}'.format(key, value))
    return '&'.join(l)


class TestApiSimple(FakeAppBase):

    def test_create_person(self):
        """
        Tests creating a person object in the cassandra database via a test api
        :return: The response from the api
        """
        first_name = generate_random_name()
        last_name = generate_random_name()
        content = {'first_name': first_name, 'last_name': last_name}
        response = self.app.post('/api/people', data=content, follow_redirects=True)
        data = json.loads(response.data)['person']
        self.assertEqual(response._status_code, 201)
        person_id = data['id']
        p = Person.objects.filter(id=person_id)
        self.assertEqual(len(p), 1)

    def test_retrieve_person(self):
        """
        Tests retrieving a person via a test api
        :return: a response object from the application
        """
        self.test_create_person()
        p = Person.objects.all().limit(1).get()
        retrieve_response = self.app.get('/api/person/{0}'.format(p.id))
        retrieve_data = json.loads(retrieve_response.data)['person']
        self.assertEqual(retrieve_response._status_code, 200)
        self.assertEqual(retrieve_data['id'], str(p.id))
        self.assertEqual(retrieve_data['first_name'], p.first_name)
        self.assertEqual(retrieve_data['last_name'], p.last_name)

    def test_update_person(self):
        """
        Tests updating a person object via a PUT API call
        :return: The response from the server
        """
        self.test_create_person()
        first_name = generate_random_name()
        last_name = generate_random_name()
        p = Person.objects.all().limit(1).get()
        updated_content = {'first_name': first_name, 'last_name': last_name}
        response = self.app.put('/api/person/{0}'.format(str(p.id)), data=updated_content)
        data = json.loads(response.data)['person']
        p = Person.objects.filter(id=data['id']).get()
        self.assertEqual(response._status_code, 200)
        self.assertEqual(p.first_name, first_name)
        self.assertEqual(p.last_name, last_name)

    def test_delete_person(self):
        """
        Tests creating and then deleting a person via the API
        :return: Response object from DELETE API call
        """
        self.test_create_person()
        p = Person.objects.all().limit(1).get()
        response = self.app.delete('/api/person/{0}'.format(str(p.id)))
        self.assertEqual(response._status_code, 204)
        self.assertRaises(DoesNotExist, Person.objects.filter(id=p.id).get)

    def test_retrieve_empty_people_list(self):
        response = self.app.get('/api/people')
        self.assertEqual(response._status_code, 200)

    def test_retrieve_many_people(self):
        """
        Creates multiple person objects via api calls and then retrieves a list of these object
        """
        count = 15
        for i in range(count):
            self.test_create_person()
        people = Person.objects.all()
        response = self.app.get('/api/people')
        data = json.loads(response.data)['people']
        self.assertEqual(response._status_code, 200)
        self.assertEqual(len(data), people.count())

    def test_retrieve_many_people_paginated(self):
        for i in range(50):
            self.app.post('/api/paginated_people',
                          data=dict(first_name=generate_random_name(), last_name=generate_random_name()),
                          follow_redirects=True)
        next_url = '/api/paginated_people'
        while next_url is not None:
            response = self.app.get(next_url)
            data = json.loads(response.data)
            next_url = data.get('meta', {}).get('next')
            if next_url is not None:
                self.assertEqual(len(data.get('paginated_people')), 2)




    # TODO: Ensure that various different types are properly evaluated (i.e. booleans, ints, etc')
    def test_create_dummy(self):
        now = datetime.now()
        content = {
            'text_': "Some Text",
            'boolean_': True,
            'int_': 10,
            'long_': 99999999999,
            'varint_': 2345,
            'datetime_': str(now - timedelta(microseconds=now.microsecond % 1000)),
            'bytes_': bytes("something"),
            'ascii_': string.ascii_letters,
            'float_': 3.14,
            'decimal_': Decimal("1.23"),
            'list_': ['list1', 'list2']
        }
        response = self.app.post('/api/dummies', data=content)
        self.assertEqual(response._status_code, 201)
        data = json.loads(response.data)['dummy']
        self.compare_dictionaries(content, data)
        return data

    def test_retrieve_dummy(self):
        data = self.test_create_dummy()
        response = self.app.get('/api/dummy/{0}'.format(data['id']))
        self.assertEqual(response._status_code, 200)
        new_data = json.loads(response.data)['dummy']
        self.compare_dictionaries(new_data, data)
        return new_data

    def test_update_dummy(self):
        data = self.test_create_dummy()
        updated_content = {'int_': 2, 'text_': 'Another Text'}
        response = self.app.put('/api/dummy/{0}'.format(data['id']), data=updated_content)
        dobj = Dummy.objects.get(id=data['id'])
        self.assertEqual(response._status_code, 200)
        self.assertEqual(dobj.int_, updated_content['int_'])
        self.assertEqual(dobj.text_, updated_content['text_'])

    def test_update_boolean(self):
        data = self.test_create_dummy()
        updated_content = {'boolean_': not data['boolean_']}
        response = self.app.put('/api/dummy/{0}'.format(data['id']), data=updated_content)
        dobj = Dummy.objects.get(id=data['id'])
        self.assertEqual(response._status_code, 200)
        self.assertEqual(dobj.boolean_, updated_content['boolean_'])

    def compare_dictionaries(self, d1, d2):
        for key, value in d1.iteritems():
            if type(value) == Decimal:
                value = float(value)
            if isinstance(value, list):
                continue
            if not isinstance(value, list) and type(d2[key]) == Decimal:
                d2[key] = float(d2[key])
            self.assertEqual(d2[key], value)


def generate_random_name():
    return ''.join(random.choice(string.letters) for _ in range(15))


if __name__ == '__main__':
    unittest.main()