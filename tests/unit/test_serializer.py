__author__ = 'Tim Martin'
from uuid import uuid1
import sys
import os
import random
import string
import logging

from cqlengine.exceptions import LWTException
from cqlengine.query import DoesNotExist
from tests.integration.helpers.managers import PersonManager
from tests.test_models import Person
from tests.base import DummyModelsBase


logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

first_names_list = ['Jonh', 'Bob', 'Mary', 'Jane', 'Joe']
last_names_list = ['Smith', 'Miller', 'Burner', 'Doe', 'The Plumber']


class TestSerializerSimple(DummyModelsBase):
    person_serializer = None

    def setUp(self):
        self.person_serializer = PersonManager()

    def test_create_person(self):
        first_name = self.generate_random_name()
        last_name = self.generate_random_name()
        p = self.person_serializer.create({'first_name': first_name, 'last_name': last_name})
        self.assertIsNotNone(p, 'No cassandra DAO was returned')
        self.assertEqual(first_name, p['first_name'])
        self.assertEqual(last_name, p['last_name'])
        self.assertIsNotNone(p['id'], 'Person does not have an id')

    def test_delete_person(self):
        first_name = self.generate_random_name()
        last_name = self.generate_random_name()
        p = self.person_serializer.create(dict(first_name=first_name, last_name=last_name))
        _id = p['id']
        self.person_serializer.delete({'id': _id})
        self.assertRaises(DoesNotExist, Person.objects.filter(id=_id).get)

        Person.objects.filter(id=_id).all()

    def test_retrieve_person(self):
        first_name = self.generate_random_name()
        last_name = self.generate_random_name()
        p = self.person_serializer.create(dict(first_name=first_name, last_name=last_name))
        p2 = self.person_serializer.retrieve({'id': p['id']})
        self.assertIsNotNone(p2, 'The person object was not effectively retrieved')
        self.assertEqual(p2['first_name'], p['first_name'])
        self.assertEqual(p2['last_name'], p['last_name'])
        self.assertEqual(p2['id'], p['id'])

    def test_update_person(self):
        first_name = self.generate_random_name()
        last_name = self.generate_random_name()
        p = self.person_serializer.create(dict(first_name=first_name, last_name=last_name))
        new_first_name = random.choice(first_names_list)
        new_last_name = random.choice(last_names_list)
        self.person_serializer.update({'id': p['id']}, {'first_name': new_first_name,
                                                        'last_name': new_last_name})
        p = self.person_serializer.retrieve({'id': p['id']})
        self.assertEqual(new_first_name, p['first_name'])
        self.assertEqual(new_last_name, p['last_name'])

    def test_create_many(self):
        batch = uuid1()
        num_randoms = 10
        num_repeats = 10
        self.person_serializer.allow_filtering = True
        for i in range(num_randoms):
            p = self.person_serializer.create(dict(first_name=self.generate_random_name(),
                                                   last_name=self.generate_random_name(),
                                                   test_batch=batch))
        consistent_first_name = self.generate_random_name()
        for i in range(num_repeats):
            p = self.person_serializer.create(dict(first_name=consistent_first_name,
                                                   last_name=self.generate_random_name(),
                                                   test_batch=batch))
        response = self.person_serializer.retrieve_list(dict(test_batch=batch))
        self.assertEqual((num_repeats+num_randoms), len(response[0]))

    def test_create_on_existing_failure(self):
        """
        Tests the transaction statement that prevents creation if the model already exists
        """
        self.person_serializer.fail_create_if_exists = True
        p = self.person_serializer.create(dict(first_name=self.generate_random_name(),
                                                       last_name=self.generate_random_name()))
        self.assertRaises(LWTException, self.person_serializer.create,
                          dict(id=p.get('id'), first_name=self.generate_random_name(), last_name=self.generate_random_name()))

    def test_create_on_existing_success(self):
        """
        Tests to ensure that the model gets overridden if .fail_create_if_exists is false
        """
        self.person_serializer.fail_create_if_exists = False
        p = self.person_serializer.create(dict(first_name=self.generate_random_name(),
                                                       last_name=self.generate_random_name()))
        p2 = self.person_serializer.create(dict(id=p.get('id'), first_name=self.generate_random_name(),
                                                        last_name=self.generate_random_name()))
        self.assertEqual(p.get('id'), p2.get('id'))
        self.assertNotEqual(p.get('first_name'), p2.get('first_name'))
        self.assertNotEqual(p.get('last_name'), p2.get('last_name'))

    def test_retrieve_many(self):
        """
        Tests the ability to retrieve many objects effectively
        """
        self.person_serializer.paginate_by = 10000000
        for i in range(30):
            self.person_serializer.create(dict(first_name=self.generate_random_name(),
                                               last_name=self.generate_random_name()))
        retrieved_list = self.person_serializer.retrieve_list({})
        self.assertEqual(len(retrieved_list[0]), Person.objects.all().count())

    def test_retrieve_many_pagination(self):
        self.person_serializer.paginate_by = 10
        for i in range(50):
            self.person_serializer.create(dict(first_name=self.generate_random_name(),
                                               last_name=self.generate_random_name()))

        pk_query_arg = self.person_serializer.pagination_pk_query_arg
        retrieved_list = self.person_serializer.retrieve_list({})
        next_pk = retrieved_list[1][pk_query_arg]
        self.assertIsNotNone(next_pk)
        self.assertEqual(len(retrieved_list[0]), self.person_serializer.paginate_by)
        while next_pk:
            retrieved_list = self.person_serializer.retrieve_list({
                pk_query_arg: next_pk
            })[0]
            next_pk = retrieved_list[1].get(pk_query_arg, None)
            if next_pk:
                self.assertEqual(len(retrieved_list[0]), self.person_serializer.paginate_by)
            else:
                self.assertLessEqual(len(retrieved_list[0]), self.person_serializer.paginate_by)

    def test_retrieve_many_pagination_arbitrary_count(self):
        self.person_serializer.paginate_by = 10
        for i in range(50):
            self.person_serializer.create(dict(first_name=self.generate_random_name(),
                                               last_name=self.generate_random_name()))

        pk_query_arg = self.person_serializer.pagination_pk_query_arg
        count_query_arg = self.person_serializer.pagination_count_query_arg
        retrieved_list = self.person_serializer.retrieve_list({})
        next_pk = retrieved_list[1][pk_query_arg]
        self.assertIsNotNone(next_pk)
        self.assertEqual(len(retrieved_list[0]), self.person_serializer.paginate_by)
        while next_pk:
            count = random.choice(range(1, 10))
            retrieved_list, status_code = self.person_serializer.retrieve_list({
                pk_query_arg: next_pk,
                count_query_arg: count
            })
            next_pk = retrieved_list[1].get(pk_query_arg)
            objects_count = len(retrieved_list[0])
            logger.debug('Retrieved count: {0}'.format(objects_count))
            if next_pk:
                self.assertEqual(len(retrieved_list[0]), count)
            else:
                self.assertLessEqual(len(retrieved_list[0]), count)

    @classmethod
    def generate_random_name(cls):
        return ''.join(random.choice(string.letters) for _ in range(15))