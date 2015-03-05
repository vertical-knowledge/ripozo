from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.relationships.relationship import Relationship
from ripozo.viewsets.constructor import ResourceMetaClass
from ripozo_tests.python2base import TestBase

import mock
import types
import unittest


class TestRelationship(TestBase, unittest.TestCase):
    """
    A TestCase for testing relationships and
    their various properties.
    """

    def test_init(self):
        """
        Tests the initialization of a Relationship instance
        In particular checking that a property map is
        always available.
        """
        r = Relationship()
        self.assertEqual(r.property_map, {})
        x = dict(some='thing')
        r = Relationship(property_map=x)
        self.assertEqual(r.property_map, x)

    def test_relation_property(self):
        """
        Tests whether the relation property is appropriately
        retrieved from ResourceMetaClass
        """
        r = Relationship()
        try:
            x = r.relation
            assert False
        except KeyError:
            assert True
        mck = mock.MagicMock(registered_names_map={'SomeClass': True})
        r = Relationship(relation='SomeClass')
        r._resource_meta_class = mck
        assert r.relation is True

    @mock.patch.object(Relationship, 'relation')
    def test_construct_resource(self, mck):
        """
        Tests the construction of a related resource
        """
        property_map = dict(parent='child')
        r = Relationship(property_map=property_map)
        prop_input = dict(parent='value')
        resource = r.construct_resource(prop_input)

        for rsrc in resource:
            self.assertIsInstance(rsrc, mock.MagicMock)
        self.assertIsInstance(resource, types.GeneratorType)
        self.assertEqual(mck.call_count, 1)
        mck.assert_called_with(properties=dict(child='value'))

        r.required = False
        resource = r.construct_resource({})
        # Should return an empty generator
        for rsrc in resource:
            assert False

        r.required = True
        # This should raise a key error since the field is required
        try:
            for rsrc in r.construct_resource({}):
                assert False
            assert False
        except KeyError:
            pass

    def test_map_pks(self):
        property_map = dict(parent='child', parent2='child2')
        original_props = dict(parent='value', parent2='value2')
        r = Relationship(property_map=property_map)
        child_properties = r._map_pks(original_props)
        expected = dict(child='value', child2='value2')
        self.assertDictEqual(child_properties, expected)
        original_props.update(dict(parent3='value3'))
        child_properties = r._map_pks(original_props)
        self.assertDictEqual(child_properties, expected)

        failing_input = dict(parent2='value2', parent3='value3')
        self.assertRaises(KeyError, r._map_pks, failing_input)

    def test_remove_child_resource_properties(self):
        property_map = dict(parent='child', parent2='child2')
        original_properties = dict(parent='value', parent2='value2',
                                   parent3='value3', parent4='value4')
        r = Relationship(property_map=property_map)
        updated_properties = r.remove_child_resource_properties(original_properties)
        self.assertNotEqual(id(updated_properties), id(original_properties))
        expected = dict(parent3='value3', parent4='value4')
        self.assertDictEqual(updated_properties, expected)

        original_properties.pop('parent2')
        updated_properties = r.remove_child_resource_properties(original_properties)
        self.assertDictEqual(updated_properties, expected)

