from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
import unittest

from ripozo.dispatch.adapters.base import AdapterBase
from ripozo.viewsets.relationships import Relationship, ListRelationship
from ripozo.viewsets.resource_base import ResourceBase

from ripozo_tests.python2base import TestBase

__author__ = 'Tim Martin'


class TestAdapter(AdapterBase):
    __abstract__ = True

    def get_formatted_body(self):
        pass

    def extra_headers(self):
        pass


class TestAdapterBase(TestBase, unittest.TestCase):
    def get_related_resource_class(self):
        class Related(ResourceBase):
            _resource_name = 'related'
            _pks = ['id']
        return Related

    def get_relationship_resource_class(self):
        class RelationshipResource(ResourceBase):
            _resource_name = 'relationship_resource'
            _relationships = {
                'relationship': Relationship(property_map=dict(id='id'), relation='Related')
            }
        return RelationshipResource

    def get_list_relationship_resource_class(self):
        class RelationshipResource(ResourceBase):
            _resource_name = 'relationship_resource'
            _relationships = {
                'relationship': ListRelationship('list_relationship', relation='Related')
            }
        return RelationshipResource

    def get_link_resource_class(self):
        class LinkResource(ResourceBase):
            _resource_name = 'link_resource'
            _links = {
                'link': Relationship('linked', relation='Related')
            }
        return LinkResource

    def get_link_list_resource_class(self):
        class LinkListResource(ResourceBase):
            _resource_name = 'link_list_resource'
            _links = {
                'link': Relationship('linked_list', relation='Related')
            }
        return LinkListResource