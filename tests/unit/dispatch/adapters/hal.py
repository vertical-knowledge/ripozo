from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.hal import HalAdapter
from tests.python2base import TestBase
from tests.unit.helpers.hello_world_viewset import HelloWorldViewset

import json
import six


class TestHalAdapter(TestBase):
    """
    Tests whether the HalAdapter appropriately creates
    a response for a resource
    """

    def setUp(self):
        self.properties = {'content': 'hello'}
        self.resource = HelloWorldViewset.hello(dict(), self.properties, {})
        self.adapter = HalAdapter(self.resource)
        self.data = json.loads(self.adapter.formatted_body)

    def test_links(self, data=None):
        """
        Tests that the _links property is available and properly formatted
        """
        if data is None:
            data = self.data
        self.assertIn('_links', data)
        self.assertIn('self', data['_links'])
        for key, value in six.iteritems(data['_links']):
            self.assertIn('href', data['_links'][key])

    def test_properties_available(self, data=None):
        """
        Tests whether all properties are available
        according to the HAL format
        """
        if data is None:
            data = self.data
        for key, value in six.iteritems(self.properties):
            self.assertIn(key, data)
            self.assertEqual(data[key], value)

    def test_embedded(self):
        """
        Tests whether the _embedded property is appropriately set.
        """
        self.assertIn('_embedded', self.data)
        embedded = self.data['_embedded']
        self.assertIsInstance(embedded, dict)
        for key, value in six.iteritems(embedded):
            # TODO need to make sure all relationships are available
            if isinstance(value, dict):
                value = [value]  # To simplify testing
            for v in value:
                self.test_links(data=v)
                # TODO need to check if properties available