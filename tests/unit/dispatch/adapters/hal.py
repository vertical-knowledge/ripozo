from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo import ResourceBase
from ripozo.dispatch.adapters.hal import HalAdapter
from ripozo.viewsets.constructor import ResourceMetaClass
from ripozo.viewsets.request import RequestContainer
from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.hello_world_viewset import get_refreshed_helloworld_viewset

import json
import six
import unittest


class TestHalAdapter(TestBase, unittest.TestCase):
    """
    Tests whether the HalAdapter appropriately creates
    a response for a resource
    """

    def setUp(self):
        ResourceMetaClass.registered_names_map.clear()
        ResourceMetaClass.registered_resource_classes.clear()
        HelloWorldViewset = get_refreshed_helloworld_viewset()

        self.properties = {'content': 'hello'}
        self.resource = HelloWorldViewset.hello(RequestContainer(query_args=dict(content='hello',
                                                                                 related='world')))
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

    def test_embedded_relationships(self):
        class Fake(ResourceBase):
            pass
        props = dict(val=1, val2=2)
        rel = Fake(properties=props)
        adapter = HalAdapter(None)
        resp = adapter._generate_relationship(rel, True)
        self.assertEqual(resp, props)

    def test_list_relationships(self):
        class Fake(ResourceBase):
            pass
        props = dict(val=1, val2=2)
        props2 = dict(val=3, val4=4)
        adapter = HalAdapter(None)
        rel1 = Fake(properties=props)
        rel2 = Fake(properties=props2)
        resp = adapter._generate_relationship([rel1, rel2], True)
        self.assertListEqual([props, props2], resp)

    def test_not_all_pks(self):
        class Fake(ResourceBase):
            _pks = ['id']

        props = dict(val=1)
        adapter = HalAdapter(None)
        rel = Fake(properties=props)
        resp = adapter._generate_relationship(rel, False)
        self.assertIsNone(resp)
