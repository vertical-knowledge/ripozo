from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest2

from ripozo.resources.relationships import Relationship, ListRelationship, FilteredRelationship
from ripozo.resources.resource_base import ResourceBase


class TestRelationships(unittest2.TestCase):
    def test_link_to_list_of_child_resources(self):
        """Tests whether there can be a relationship
        That simply provides a link to a list of the children of
        the resource.  In otherwords, they are not embedded in any
        way.  Not even the child links"""
        class Parent(ResourceBase):
            pks = 'id',
            _relationships = Relationship('children', relation='Child',
                                          property_map=dict(id='parent_id'),
                                          query_args=['parent_id'], no_pks=True,
                                          remove_properties=False),

        class Child(ResourceBase):
            resource_name = 'child'
            pks = 'id',

        props = dict(id=1, name='something')
        parent = Parent(properties=props)
        link_to_children = parent.related_resources[0].resource
        self.assertEqual(link_to_children.url, '/child?parent_id=1')
        self.assertEqual(parent.url, '/parent/1')

    def test_filter_relationship(self):
        """Same as `test_link_to_list_of_children` but using the
        `FilteredRelationship` class"""
        class Parent(ResourceBase):
            pks = 'id',
            _relationships = FilteredRelationship('children', relation='Child',
                                                  property_map=dict(id='parent_id')),

        class Child(ResourceBase):
            resource_name = 'child'
            pks = 'id',

        props = dict(id=1, name='something')
        parent = Parent(properties=props)
        link_to_children = parent.related_resources[0].resource
        self.assertEqual(link_to_children.url, '/child?parent_id=1')
        self.assertEqual(parent.url, '/parent/1')
