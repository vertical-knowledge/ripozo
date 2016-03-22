from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import unittest2

from ripozo import RequestContainer
from ripozo.adapters.base import AdapterBase
from ripozo.exceptions import RestException
from ripozo.resources.relationships import Relationship, ListRelationship
from ripozo.resources.resource_base import ResourceBase
from ripozo_tests.unit.tests.constructrequesthelper import TestConstructRequestHelper

class TestAdapter(AdapterBase):
    __abstract__ = True
    formats = ['blah']

    @property
    def formatted_body(self):
        return super(TestAdapter, self).formatted_body

    @property
    def extra_headers(self):
        return super(TestAdapter, self).extra_headers


class TestAdapterBase(unittest2.TestCase, TestConstructRequestHelper):
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

    def test_coverage_annoyance(self):
        """
        Just hitting the NotImplementErrors so I don't get
        annoyed anymore.
        """
        adapter = TestAdapter(None)
        try:
            x = adapter.formatted_body
            assert False
        except NotImplementedError:
            assert True

        try:
            x = adapter.extra_headers
            assert False
        except NotImplementedError:
            assert True

    def test_format_exception(self):
        """
        Tests the format_exception class method.
        """
        exc = RestException('blah blah', status_code=458)
        json_dump, content_type, status_code = TestAdapter.format_exception(exc)
        data = json.loads(json_dump)
        self.assertEqual(TestAdapter.formats[0], content_type)
        self.assertEqual(status_code, 458)
        self.assertEqual(data['message'], 'blah blah')

    def test_format_request(self):
        """Dumb test for format_request"""
        request = RequestContainer()
        response = TestAdapter.format_request(request)
        self.assertIs(response, request)

    def test_construct_request_from_wsgi_environ(self):
        self.construct_request_from_wsgi_environ(AdapterBase)
