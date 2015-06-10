from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import NotFoundException

import logging
import random
import six
import string
import uuid


def logger():
    return logging.getLogger(__name__)


def generate_random_name():
    return ''.join(random.choice(string.ascii_letters) for _ in range(15))


class TestManagerMixin(object):
    """
    manager, does_not_exist_exception, and all_person_models proeprties need to be implemented
    get_person_model_by_id method needs to be implemented
    """

    @property
    def manager(self):
        """

        :return:
        :rtype: ripozo.managers.base.BaseManager
        """
        raise NotImplementedError

    @property
    def model_pks(self):
        """

        :return:
        :rtype: dict
        """
        raise NotImplementedError

    def assertValuesEqualModel(self, model, values):
        # TODO docs
        raise NotImplementedError

    def assertValuesNotEqualsModel(self, model, values):
        # TODO docs
        raise NotImplementedError

    def create_model(self, values=None):
        # TODO docs
        raise NotImplementedError

    def get_model(self, values):
        # TODO docs
        # Should raise exception when not found
        raise NotImplementedError

    def get_model_pks(self, model):
        # TODO docs
        raise NotImplementedError

    def get_values(self, defaults=None):
        # TODO docs
        raise NotImplementedError

    def assertResponseValid(self, resp, init_values, valid_fields=None):
        valid_fields = valid_fields or self.manager.fields
        for key, value in six.iteritems(init_values):
            if key not in valid_fields:
                self.assertTrue(key not in resp)
            else:
                self.assertEqual(resp[key], init_values[key])

    def get_random_pks(self):
        pks_dict = dict()
        for pk in self.model_pks:
            pks_dict[pk] = uuid.uuid4()
        return pks_dict

    def test_create(self):
        """
        Tests that the model is appropriately created
        """
        new_values = self.get_values()
        resp = self.manager.create(new_values)
        self.assertResponseValid(resp, new_values, valid_fields=self.manager.create_fields)

    def test_retrieve(self):
        """
        Tests that a model can be appropriately retrieved
        """
        new_values = self.get_values()
        model = self.create_model(values=new_values)
        pks = self.get_model_pks(model)
        resp = self.manager.retrieve(pks)
        self.assertResponseValid(resp, new_values)

    def test_retrieve_not_found(self):
        """
        Tests that NotFoundException is raised when
        a model is not found.
        """
        self.assertRaises(NotFoundException, self.manager.retrieve, self.get_random_pks())

    def test_update(self):
        """
        Tests that a model is appropriately updated
        """
        values = self.get_values()
        old_values = values.copy()
        model = self.create_model(values=values)
        updated_values = self.get_values()
        resp = self.manager.update(self.get_model_pks(model), updated_values)
        self.assertValuesEqualModel(model, updated_values)
        self.assertValuesNotEqualsModel(model, old_values)
        self.assertResponseValid(resp, updated_values)

    def test_update_not_exists(self):
        """
        Tests that a DoesNotExistException exception
        is raised if the model does not exists
        """
        new_values = self.get_values()
        pks_dict = self.get_random_pks()
        self.assertRaises(NotFoundException, self.manager.update, pks_dict, new_values)

    def test_retrieve_list(self):
        """
        Tests that the retrieve_list appropriately
        returns a list of resources
        """
        new_count = 10
        for i in range(new_count):
            self.create_model()
        resp, meta = self.manager.retrieve_list({})
        if new_count > self.manager.paginate_by:
            self.assertEqual(len(resp), self.manager.paginate_by)
        else:
            self.assertGreaterEqual(len(resp), new_count)
        for r in resp:
            for key, value in six.iteritems(r):
                self.assertIn(key, self.manager.list_fields)

    def test_retrieve_empty_list(self):
        """
        Tests that an empty list is returned if
        no results match.
        """
        pks = self.get_random_pks()
        resp, meta = self.manager.retrieve_list(pks)
        self.assertEqual(len(resp), 0)

    def test_retrieve_filtering(self):
        """
        Tests that the basic filtering works
        for the manager
        """
        raise NotImplementedError

    def test_retrieve_list_paginations(self):
        """
        Tests that the pagination works correctly with
        retrieve_list
        """
        paginate_by = 3
        original = self.manager.paginate_by
        self.manager.paginate_by = paginate_by
        try:
            for i in range(paginate_by * 3 + 1):
                self.create_model()
            resp, meta = self.manager.retrieve_list({})
            self.assertEqual(len(resp), paginate_by)
            links = meta['links']
            self.assertIn('next', links)
            next_count = 0
            while 'next' in links:
                next_count += 1
                resp, meta = self.manager.retrieve_list(links['next'])
                self.assertLessEqual(len(resp), paginate_by)
                links = meta['links']

            prev_count = 0
            self.assertIn('previous', links)
            while 'previous' in links:
                prev_count += 1
                resp, meta = self.manager.retrieve_list(links['previous'])
                self.assertLessEqual(len(resp), paginate_by)
                links = meta['links']

            self.assertEqual(prev_count, next_count)
        finally:
            self.manager.paginate_by = original

    def test_delete(self):
        """
        Tests that a resource is deleted appropriately.
        """
        model = self.create_model()
        model_pks = self.get_model_pks(model)
        resp = self.manager.delete(model_pks)
        self.assertRaises(Exception, self.get_model, model_pks)
        # TODO assert response value

    def test_delete_not_exists(self):
        """
        Tests that a DoesNotExistException exception
        is raised if the model does not exists
        """
        self.assertRaises(NotFoundException, self.manager.delete, self.get_random_pks())

    def test_get_field(self):
        """
        Tests that the
        :return:
        :rtype:
        """
