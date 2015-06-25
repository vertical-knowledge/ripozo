from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.manager_base import BaseManager

import six
import unittest2


class FakeManager(BaseManager):
    def create(self, values, *args, **kwargs):
        pass

    def retrieve(self, lookup_keys, *args, **kwargs):
        pass

    def retrieve_list(self, filters, *args, **kwargs):
        pass

    def update(self, lookup_keys, updates, *args, **kwargs):
        pass

    def delete(self, lookup_keys, *args, **kwargs):
        pass


class TestBaseManager(unittest2.TestCase):
    def test_fields(self):
        m = FakeManager()
        self.assertListEqual(m.fields, [])

    def test_create_fields(self):
        m = FakeManager()
        self.assertListEqual(m.create_fields, [])

    def test_list_fields(self):
        m = FakeManager()
        self.assertListEqual(m.list_fields, [])

    def test_update_fields(self):
        m = FakeManager()
        self.assertListEqual(m.update_fields, [])

    def test_field_validators(self):
        class M(FakeManager):
            fields = ('x', 'y', 'z',)
            _field_validators = dict(x=1, z=2)

        resp = M.field_validators
        for x in [None, 1, 2]:
            self.assertIn(x, resp)

    def test_valid_fields(self):
        """
        Tests the valid fields method.
        """
        original_values = dict(x=1, y=2, z=3)
        valid_fields = ['x', 'z', 'q']
        resp = BaseManager.valid_fields(original_values, valid_fields)
        self.assertDictEqual(resp, dict(x=1, z=3))

    def test_dot_field_list_to_dict(self):
        """
        Tests the appropriate dictionary return
        """
        class Manager(FakeManager):
            pass

        input_outputs = [
            ([], {}),
            (['blah'], {'blah': None}),
            (['blah', 'a.b', 'a.c'], {'blah': None, 'a': {'b': None, 'c': None}})
        ]
        for method_input, output in input_outputs:
            generated = Manager().dot_field_list_to_dict(method_input)
            self.assertDictEqual(generated, output)

    def test_get_pagination_pks(self):
        m = FakeManager()
        self.assertEqual(None, m.get_pagination_pks(dict())[0])
        self.assertEqual(1, m.get_pagination_pks(dict(pagination_pk=1))[0])

    def test_get_pagination_count(self):
        m = FakeManager()
        self.assertEqual(m.paginate_by, m.get_pagination_count(dict())[0])
        self.assertEqual(1, m.get_pagination_count(dict(count=1))[0])
