from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.relationships.relationship import Relationship
from ripozo.viewsets.resource_base import ResourceBase
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
        r = Relationship('related')
        self.assertEqual(r.property_map, {})
        x = dict(some='thing')
        r = Relationship('related', property_map=x)
        self.assertEqual(r.property_map, x)

    def test_relation_property(self):
        """
        Tests whether the relation property is appropriately
        retrieved from ResourceMetaClass
        """
        r = Relationship('related')
        try:
            x = r.relation
            assert False
        except KeyError:
            assert True
        mck = mock.MagicMock(registered_names_map={'SomeClass': True})
        r = Relationship('related', relation='SomeClass')
        r._resource_meta_class = mck
        assert r.relation is True

    def test_construct_resource(self):
        """
        Tests the construction of a related resource
        """
        class RelatedResource(ResourceBase):
            pass

        property_map = dict(parent='child')
        r = Relationship('related', property_map=property_map, relation='RelatedResource')
        prop_input = dict(parent='value')
        resource = r.construct_resource(prop_input)

        self.assertIsInstance(resource, RelatedResource)

        r.required = False
        resource = r.construct_resource({})
        self.assertIsNone(resource)

        r.required = True
        # This should raise a key error since the field is required
        try:
            for rsrc in r.construct_resource({}):
                assert False
            assert False
        except KeyError:
            pass

    def test_map_pks(self):
        # TODO this should probably be redone
        property_map = dict(parent='child', parent2='child2')
        original_props = dict(parent='value', parent2='value2')
        r = Relationship('related', property_map=property_map)
        child_properties = r._map_pks(original_props)
        expected = dict(child='value', child2='value2')
        self.assertDictEqual(child_properties, expected)

    def test_remove_child_resource_properties(self):
        property_map = dict(parent='child', parent2='child2')
        original_properties = dict(parent='value', parent2='value2',
                                   parent3='value3', parent4='value4')
        r = Relationship('related', property_map=property_map)
        updated_properties = r.remove_child_resource_properties(original_properties)
        self.assertNotEqual(id(updated_properties), id(original_properties))
        expected = dict(parent3='value3', parent4='value4')
        self.assertDictEqual(updated_properties, expected)

        original_properties.pop('parent2')
        updated_properties = r.remove_child_resource_properties(original_properties)
        self.assertDictEqual(updated_properties, expected)

