from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.boring_json import BoringJSONAdapter
from ripozo.viewsets.request import RequestContainer
from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.hello_world_viewset import  get_refreshed_helloworld_viewset

import json
import six
import unittest


class TestBoringJSONAdapter(TestBase, unittest.TestCase):
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

        for relationship, field_name, embedded in self.resource.relationships:
            self.assertIn(field_name, data)
