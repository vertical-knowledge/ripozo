from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.boring_json import BoringJSONAdapter
from tests.python2base import TestBase
from tests.unit.helpers.hello_world_viewset import HelloWorldViewset

import json
import six


class TestBoringJSONAdapter(TestBase):
    """
    Tests whether the BoringJSONAdapter appropriately creates
    a response for a resource
    """
    # TODO this definitely needs to be fleshed out.  All of it.

    def setUp(self):
        self.properties = {'content': 'hello'}
        self.resource = HelloWorldViewset.hello(dict(), self.properties, {})
        self.adapter = BoringJSONAdapter(self.resource)
        self.data = json.loads(self.adapter.formatted_body)

    def test_properties_available(self):
        data = self.data[self.resource.resource_name]
        for key, value in six.iteritems(self.properties):
            self.assertIn(key, data)
            self.assertEqual(value, data[key])

        for field_name, relationship in six.iteritems(self.resource.relationships):
            self.assertIn(field_name, data)
