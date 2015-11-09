from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import RestException
from ripozo.resources.relationships.relationship import Relationship
from ripozo.resources.resource_base import ResourceBase

import mock
import unittest2


class TestRelationship(unittest2.TestCase):
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

        self.assertIsNotNone(resource)

        r.required = True
        # This should raise a key error since the field is required
        self.assertRaises(RestException, r.construct_resource, {})

    def test_relationship_generation(self):
        """Tests the generation of relationships in the ResourceBase"""
        class MyResource3(ResourceBase):
            _relationships = [Relationship('related', relation='RelatedResource3')]

        class RelatedResource3(ResourceBase):
            _pks = ['pk']

        resource = MyResource3(properties=dict(id=1, related=dict(pk=2)))
        self.assertDictEqual(resource.properties, dict(id=1))
        self.assertEqual(len(resource.related_resources), 1)
        relation = resource.related_resources[0]
        related_res = relation[0]
        self.assertIsInstance(related_res, RelatedResource3)
        self.assertDictEqual(related_res.properties, dict(pk=2))

    def test_relationship_generation_with_dict_literal(self):
        """
        For some reason it breaks when you use brackets
        to define the dictionary
        """
        class MyResource2(ResourceBase):
            _relationships = [Relationship('related', relation='RelatedResource2')]

        class RelatedResource2(ResourceBase):
            _pks = ['pk']

        resource = MyResource2(properties={'id': 1, 'related': {'pk': 2}})
        self.assertEqual(resource.properties, dict(id=1))
        self.assertEqual(len(resource.related_resources), 1)
        relation = resource.related_resources[0]
        related_res = relation[0]
        self.assertIsInstance(related_res, RelatedResource2)
        self.assertEqual(related_res.properties, dict(pk=2))

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

    def test_return_none(self):
        """Tests that the private _should_return_none appropriately
        returns according to the expected behavior"""
        class MyResource(ResourceBase):
            pks = 'id',

        res = MyResource(no_pks=True)
        rel = Relationship('related')
        self.assertFalse(rel._should_return_none(res))
        res = MyResource(properties=dict(id=1))
        self.assertFalse(rel._should_return_none(res))
        res = MyResource(properties=dict())
        self.assertTrue(rel._should_return_none(res))
        rel.templated = True
        self.assertFalse(rel._should_return_none(res))

    def test_remove_properties(self):
        """Tests whether properties are appropriately
        kept or removed according to the remove_properties
        attribute"""
        rel = Relationship('related')
        x = dict(related=dict(name='name'))
        ret = rel._map_pks(x)
        self.assertDictEqual(ret, dict(name='name'))
        self.assertDictEqual(x, dict())
        rel.remove_properties = False
        x = dict(related=dict(name='name'))
        ret = rel._map_pks(x)
        self.assertDictEqual(ret, dict(name='name'))
        self.assertDictEqual(x, dict(related=dict(name='name')))

    def test_remove_properties_property_map(self):
        """Tests whether removing properties according
        to the property_map adheres to the remove_properties
        attribute"""

        rel = Relationship('related', property_map=dict(name='name'))
        x = dict(name='name')
        ret = rel._map_pks(x)
        self.assertDictEqual(ret, dict(name='name'))
        self.assertDictEqual(x, dict())
        rel.remove_properties = False
        x = dict(name='name')
        ret = rel._map_pks(x)
        self.assertDictEqual(ret, dict(name='name'))
        self.assertDictEqual(x, dict(name='name'))
