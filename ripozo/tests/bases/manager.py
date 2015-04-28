from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.tests.python2base import TestBase

import logging
import random
import string


def logger():
    return logging.getLogger(__name__)


def generate_random_name():
    return ''.join(random.choice(string.ascii_letters) for _ in range(15))


class TestManagerMixin(TestBase):
    """
    manager, does_not_exist_exception, and all_person_models proeprties need to be implemented
    get_person_model_by_id method needs to be implemented
    """
    first_name_field = 'first_name'
    last_name_field = 'last_name'
    id_field = 'id'
    _manager = None

    def setUp(self):
        self._manager = self.manager

    @property
    def manager(self):
        """
        Return the serializer for the specific implementation

        :rtype: rest.managers.base.BaseManager
        """
        raise NotImplementedError

    @property
    def does_not_exist_exception(self):
        """
        return the exception type that is raised when the model does not exist
        """
        raise NotImplementedError

    @property
    def all_person_models(self):
        """
        :return: Every single person model
        :rtype: list
        """
        raise NotImplementedError

    def get_person_model_by_id(self, person_id):
        """
        Directly query the data base for a person model with the id specified
        """
        raise NotImplementedError

    def test_create_person(self):
        first_name = generate_random_name()
        last_name = generate_random_name()
        person = self._manager.create({self.first_name_field: first_name,
                                      self.last_name_field: last_name})
        self.assertIsNotNone(person)
        self.assertEqual(first_name, person[self.first_name_field])
        self.assertEqual(last_name, person[self.last_name_field])
        self.assertIsNotNone(person[self.id_field])

    def test_delete_person(self):
        first_name = generate_random_name()
        last_name = generate_random_name()
        p = self._manager.create({self.first_name_field: first_name,
                                 self.last_name_field: last_name})
        _id = p[self.id_field]
        self._manager.delete({self.id_field: _id})
        self.assertRaises(self.does_not_exist_exception, self.get_person_model_by_id, _id)

    def test_retrieve_person(self):
        first_name = generate_random_name()
        last_name = generate_random_name()
        p = self._manager.create({self.first_name_field: first_name,
                                 self.last_name_field: last_name})
        p2 = self._manager.retrieve({self.id_field: p[self.id_field]})
        self.assertIsNotNone(p2)
        self.assertEqual(p2[self.first_name_field], p[self.first_name_field])
        self.assertEqual(p2[self.last_name_field], p[self.last_name_field])
        self.assertEqual(p2[self.id_field], p[self.id_field])

    def test_update_person(self):
        first_name = generate_random_name()
        last_name = generate_random_name()
        p = self._manager.create({self.first_name_field: first_name,
                                 self.last_name_field: last_name})
        new_first_name = generate_random_name()
        new_last_name = generate_random_name()
        self._manager.update({self.id_field: p[self.id_field]},
                             {self.first_name_field: new_first_name,
                              self.last_name_field: new_last_name})
        p2 = self._manager.retrieve({self.id_field: p[self.id_field]})
        self.assertEqual(new_first_name, p2[self.first_name_field])
        self.assertEqual(new_last_name, p2[self.last_name_field])
        self.assertNotEqual(first_name, p2[self.first_name_field])
        self.assertNotEqual(last_name, p2[self.last_name_field])

    def test_create_many(self):
        num_randoms = 10
        for i in range(num_randoms):
            self._manager.create({self.first_name_field: generate_random_name(),
                                 self.last_name_field: generate_random_name()})
        response = self._manager.retrieve_list({})
        self.assertEqual(num_randoms, len(list(response[0])))

        # Check the meta response
        meta = response[1]
        self.assertIn(self._manager.pagination_pk_query_arg, meta)
        self.assertIn(self._manager.pagination_count_query_arg, meta)
        self.assertIn(self._manager.pagination_next, meta)

    def test_retrieve_many(self):
        """
        Tests the ability to retrieve many objects effectively
        """
        manager = self._manager
        manager.paginate_by = 1000000
        for i in range(30):
            manager.create({self.first_name_field: generate_random_name(),
                            self.last_name_field: generate_random_name()})
        retrieved_list = manager.retrieve_list({})
        self.assertEqual(len(retrieved_list[0]), len(self.all_person_models))

    def test_retrieve_many_pagination(self):
        manager = self._manager
        manager.paginate_by = 10
        for i in range(50):
            manager.create(dict(first_name=generate_random_name(),
                                last_name=generate_random_name()))

        pk_query_arg = manager.pagination_pk_query_arg
        retrieved_list = manager.retrieve_list({})
        next_pk = retrieved_list[1][pk_query_arg]
        self.assertIsNotNone(next_pk)
        self.assertEqual(len(retrieved_list[0]), manager.paginate_by)
        while next_pk:
            retrieved_list = manager.retrieve_list({
                pk_query_arg: next_pk
            })[0]
            next_pk = retrieved_list[1].get(pk_query_arg, None)
            if next_pk:
                self.assertEqual(len(retrieved_list[0]), manager.paginate_by)
            else:
                self.assertLessEqual(len(retrieved_list[0]), manager.paginate_by)

    def test_retrieve_many_pagination_arbitrary_count(self):
        manager = self._manager
        manager.paginate_by = 10
        for i in range(50):
            manager.create(dict(first_name=generate_random_name(),
                                last_name=generate_random_name()))

        pk_query_arg = manager.pagination_pk_query_arg
        count_query_arg = manager.pagination_count_query_arg
        retrieved_list, meta = manager.retrieve_list({})
        next_pk = meta[pk_query_arg]
        self.assertIsNotNone(next_pk)
        self.assertEqual(len(retrieved_list), manager.paginate_by)
        count = random.choice(range(1, 10))
        while next_pk:
            retrieved_list, meta = manager.retrieve_list({
                pk_query_arg: next_pk,
                count_query_arg: count
            })
            next_pk = meta.get(pk_query_arg)
            objects_count = len(retrieved_list)
            logger().debug('Retrieved count: {0}'.format(objects_count))
            if next_pk:
                self.assertEqual(len(retrieved_list), count)
            else:
                self.assertLessEqual(len(retrieved_list), count)