from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.siren import SirenAdapter
from ripozo.viewsets.relationships import Relationship, ListRelationship
from ripozo.viewsets.request import RequestContainer
from ripozo.viewsets.resource_base import ResourceBase

from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.hello_world_viewset import get_refreshed_helloworld_viewset

from tests.unit.dispatch.adapters.base import TestAdapterBase

import json
import six
import unittest


class TestSirenAdapter(TestAdapterBase):
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

    def test_links_single(self):
        """
        Tests getting the links attribute for
        """
        class LinkResource(ResourceBase):
            _links = {
                'first_link': Relationship(name='first_link', relation='RelatedResource')
            }

        class RelatedResource(ResourceBase):
            pks = ['id']

        meta = dict(links=dict(
            first_link=dict(id=1),
            second_link=dict()
        ))

        lr = LinkResource(meta=meta)
        adapter = SirenAdapter(lr)
        data = json.loads(adapter.formatted_body)
        links = data['links']
        self.assertEqual(len(links), 3)

        first_link = None
        second_link = None
        self_ref = None
        for link in links:
            if 'self' in link['rel']:
                self_ref = link['href']
            elif 'second_link' in link['rel']:
                second_link = link['href']
            elif 'first_link' in link['rel']:
                first_link = link['href']
        self.assertIsNotNone(second_link)
        self.assertIsNotNone(self_ref)
        self.assertIsNotNone(first_link)
        self.assertEqual(self_ref, '/link_resource')
        self.assertEqual(first_link, '/related_resource/1')
        self.assertEqual(second_link, '/link_resource')

    def test_relationship_single(self):
        class RelationshipResource(ResourceBase):
            _relationships = {
                'first_link': Relationship(name='first_link', relation='RelatedResource'),
                'second_link': Relationship(name='second_link', relation='RelatedResource', embedded=True)
            }

        class RelatedResource(ResourceBase):
            pks = ['id']

        properties = dict(
            first_link=dict(
                id=1,
                prop='another'
            ),
            second_link=dict(
                id=2,
                prop='value'
            )
        )
        lr = RelationshipResource(properties=properties)
        adapter = SirenAdapter(lr)
        data = json.loads(adapter.formatted_body)
        entities = data['entities']
        has_second = False
        has_first = False
        for ent in entities:
            if 'second_link' in ent['rel']:
                self.assertIn('properties', ent)
                self.assertEqual(ent['properties']['id'], 2)
                self.assertEqual(ent['properties']['prop'], 'value')
                has_second = True
            elif 'first_link' in ent['rel']:
                assert 'properties' not in ent
                self.assertEqual(ent['href'], '/related_resource/1')
                has_first = True
        self.assertTrue(has_first)
        self.assertTrue(has_second)
