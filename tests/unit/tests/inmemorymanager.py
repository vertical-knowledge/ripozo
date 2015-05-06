from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.tests.bases.manager import TestManagerMixin
from ripozo.tests.helpers.inmemory_manager import InMemoryManager
from ripozo.tests.python2base import TestBase

import unittest


class InMemoryManagerBaseTestMixin(TestManagerMixin):
    @property
    def manager(self):
        return self._manager

    @property
    def model_pks(self):
        return ['id']

    def get_model(self, values):
        key = values.values()[0]
        return self.manager.objects[key]

    def assertValuesEqualModel(self, model, values):
        self.assertDictEqual(model, values)

    def assertValuesNotEqualsModel(self, model, values):
        self.assertRaises(Exception, self.assertDictEqual, model, values)

    def get_model_pks(self, model):
        return dict(id=model['id'])

    def get_values(self, defaults=None):
        raise NotImplementedError

    def create_model(self, values=None):
        raise NotImplementedError


class TestInMemoryManager(InMemoryManagerBaseTestMixin, unittest.TestCase):
    def get_values(self, defaults=None):
        values = dict(id=self.random_string(), value1=self.random_string(), value2=self.random_string())
        if defaults:
            values.update(defaults)
        return values

    def create_model(self, values=None):
        values = values or self.get_values()
        self.manager.objects[values['id']] = values
        return values

    def setUp(self):
        class FakeManager(InMemoryManager):
            _fields = ['id', 'value1', 'value2']

        self._manager = FakeManager()

    def test_retrieve_filtering(self):
        defaults = dict(value1=self.random_string())
        same_value1_count = 5
        for i in range(same_value1_count):
            self.create_model(values=self.get_values(defaults=defaults))
        resp, meta = self.manager.retrieve_list({})
        self.assertEqual(len(resp), same_value1_count)
        for r in resp:
            self.assertEqual(defaults['value1'], r['value1'])