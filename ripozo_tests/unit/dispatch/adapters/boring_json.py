from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import six
import unittest2

from ripozo.adapters import BoringJSONAdapter
from ripozo.resources.request import RequestContainer
from ripozo_tests.helpers.hello_world_viewset import get_refreshed_helloworld_viewset


class TestBoringJSONAdapter(unittest2.TestCase):
    """
    Tests whether the BoringJSONAdapter appropriately creates
    a response for a resource
    """
    # TODO this definitely needs to be fleshed out.  All of it.

    def setUp(self):
        HelloWorldViewset = get_refreshed_helloworld_viewset()

        self.properties = {'content': 'hello'}
        self.resource = HelloWorldViewset.hello(RequestContainer(query_args=dict(content='hello',
                                                                                 related='world')))
        self.adapter = BoringJSONAdapter(self.resource)
        self.data = json.loads(self.adapter.formatted_body)

    def test_properties_available(self):
        data = self.data[self.resource.resource_name]
        for key, value in six.iteritems(self.properties):
            self.assertIn(key, data)
            self.assertEqual(value, data[key])

        for relationship, field_name, embedded in self.resource.related_resources:
            self.assertIn(field_name, data)

    def test_content_header(self):
        adapter = BoringJSONAdapter(None)
        self.assertEqual(adapter.extra_headers, {'Content-Type': 'application/json'})
