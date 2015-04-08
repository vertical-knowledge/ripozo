from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.siren import SirenAdapter
from ripozo.viewsets.request import RequestContainer
from ripozo.viewsets.resource_base import ResourceBase

from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.hello_world_viewset import get_refreshed_helloworld_viewset

import json
import six
import unittest


class TestSirenAdapter(TestBase, unittest.TestCase):
    """
    Tests whether the SirenAdapter appropriately adds
    creates a resource
    """

    def setUp(self):
        HelloWorldViewset = get_refreshed_helloworld_viewset()
        self.resource = HelloWorldViewset.hello(RequestContainer(query_args={'content': 'hello', 'related': 'world'}))
        self.adapter = SirenAdapter(self.resource, base_url='http://localhost:')
        self.data = json.loads(self.adapter.formatted_body)

    def test_class_available(self):
        """
        Ensures the class property is available and appropriate
        """
        self.assertIsInstance(self.adapter.formatted_body, six.string_types)
        self.assertIn('class', self.data)
        classes = self.data['class']
        self.assertIsInstance(classes, list)
        for c in classes:
            self.assertIsInstance(c, six.string_types)

    def test_properties_available(self):
        """
        Ensures that the properties attribute is available
        and is a dictionary
        """
        self.assertIn('properties', self.data)
        props = self.data['properties']
        self.assertIsInstance(props, dict)

    def test_entities_available(self):
        self.assertIn('entities', self.data)
        entities = self.data['entities']
        self.assertIsInstance(entities, list)
        for ent in entities:
            self.assertIsInstance(ent, dict)
            # TODO actually check the entities

    def test_actions_available(self):
        """
        Tests whether the entities are available and valid
        """
        # TODO check whether all actions are available
        self.assertIn('actions', self.data)
        actions = self.data['actions']
        self.assertIsInstance(actions, list)
        for a in actions:
            self.assertIsInstance(a, dict)
            self.assertIn('href', a)
            self.assertIsInstance(a['href'], six.text_type)
            self.assertIn('method', a)
            self.assertIsInstance(a['method'], six.text_type)
            self.assertIn('name', a)
            self.assertIsInstance(a['name'], six.text_type)
            # TODO check actions

    def test_links_available(self):
        """
        Tests whether the links attribute is available and
        if there is a self referential link
        """
        self.assertIn('links', self.data)
        links = self.data['links']
        self.assertIsInstance(links, list)
        for l in links:
            self.assertIsInstance(l, dict)
            self.assertIn('rel', l)
            self.assertIsInstance(l['rel'], list)
            self.assertIn('href', l)
            self.assertIsInstance(l['href'], six.text_type)

    def test_empty_response(self):
        """
        Tests whether an empty body is returned when the status_code
        is 204
        """
        class T1(ResourceBase):
            _resource_name = 'blah'

        res = T1(properties=dict(x='something'), status_code=204)
        adapter = SirenAdapter(res)
        self.assertEqual(adapter.formatted_body, '')