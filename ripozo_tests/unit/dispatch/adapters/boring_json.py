from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import six
import unittest2

from ripozo import ResourceBase
from ripozo.adapters import BasicJSONAdapter
from ripozo.exceptions import RestException
from ripozo.resources.request import RequestContainer
from ripozo_tests.helpers.hello_world_viewset import get_refreshed_helloworld_viewset
from ripozo_tests.unit.tests.constructrequesthelper import TestConstructRequestHelper


class TestBoringJSONAdapter(unittest2.TestCase, TestConstructRequestHelper):
    """
    Tests whether the BasicJSONAdapter appropriately creates
    a response for a resource
    """
    # TODO this definitely needs to be fleshed out.  All of it.

    def setUp(self):
        HelloWorldViewset = get_refreshed_helloworld_viewset()

        self.properties = {'content': 'hello'}
        self.resource = HelloWorldViewset.hello(RequestContainer(query_args=dict(content='hello',
                                                                                 related='world')))
        self.adapter = BasicJSONAdapter(self.resource)
        self.data = json.loads(self.adapter.formatted_body)

    def test_properties_available(self):
        data = self.data[self.resource.resource_name]
        for key, value in six.iteritems(self.properties):
            self.assertIn(key, data)
            self.assertEqual(value, data[key])

        for relationship, field_name, embedded in self.resource.related_resources:
            self.assertIn(field_name, data)

    def test_content_header(self):
        adapter = BasicJSONAdapter(None)
        self.assertEqual(adapter.extra_headers, {'Content-Type': 'application/json'})

    def test_format_exception(self):
        """
        Tests the format_exception class method.
        """
        exc = RestException('blah blah', status_code=458)
        json_dump, content_type, status_code = BasicJSONAdapter.format_exception(exc)
        data = json.loads(json_dump)
        self.assertEqual(BasicJSONAdapter.formats[0], content_type)
        self.assertEqual(status_code, 458)
        self.assertEqual(data['message'], 'blah blah')

    def test_format_request(self):
        """Dumb test for format_request"""
        request = RequestContainer()
        response = BasicJSONAdapter.format_request(request)
        self.assertIs(response, request)

    def test_append_relationships_to_list_list_relationship(self):
        """
        Tests whether the relationships are appropriately
        added to the response
        """
        class MyResource(ResourceBase):
            pass

        relationship_list = [MyResource(properties=dict(id=1)), MyResource(properties=dict(id=2))]
        relationships = [(relationship_list, 'name', True)]
        rel_dict = {}
        BasicJSONAdapter._append_relationships_to_list(rel_dict, relationships)
        self.assertDictEqual(dict(name=[dict(id=1), dict(id=2)]), rel_dict)

    def test_append_relationships_to_list_single_relationship(self):
        """
        Ensures that a Relationship (not ListRelationship) is properly added
        """
        class MyResource(ResourceBase):
            pass

        relationships = [(MyResource(properties=dict(id=1)), 'name', True)]
        rel_dict = {}
        BasicJSONAdapter._append_relationships_to_list(rel_dict, relationships)
        self.assertDictEqual(dict(name=[dict(id=1)]), rel_dict)

    def test_construct_request_from_wsgi_environ(self):
        self.construct_request_from_wsgi_environ(BasicJSONAdapter)
