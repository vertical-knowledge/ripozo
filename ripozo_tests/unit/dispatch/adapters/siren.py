from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import mock
import six

from ripozo.adapters import SirenAdapter
from ripozo.exceptions import RestException
from ripozo.resources.relationships import Relationship, ListRelationship
from ripozo.resources.request import RequestContainer
from ripozo.resources.resource_base import ResourceBase
from ripozo.resources.constants import input_categories
from ripozo_tests.helpers.hello_world_viewset import get_refreshed_helloworld_viewset
from ripozo_tests.unit.dispatch.adapters.base import TestAdapterBase


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
            _links = [
                Relationship('first_link', relation='RelatedResource')
            ]

        class RelatedResource(ResourceBase):
            pks = ['id']

        meta = dict(links=dict(
            first_link=dict(id=1),
            ignored_link=dict()
        ))

        lr = LinkResource(meta=meta)
        adapter = SirenAdapter(lr)
        data = json.loads(adapter.formatted_body)
        links = data['links']
        self.assertEqual(len(links), 2)

        first_link = None
        self_ref = None
        for link in links:
            if 'self' in link['rel']:
                self_ref = link['href']
            elif 'first_link' in link['rel']:
                first_link = link['href']
        self.assertIsNotNone(self_ref)
        self.assertIsNotNone(first_link)
        self.assertEqual(self_ref, '/link_resource')
        self.assertEqual(first_link, '/related_resource/1')

    def test_relationship_single(self):
        class RelationshipResource(ResourceBase):
            _relationships = [
                Relationship('first_link', relation='RelatedResource'),
                Relationship('second_link', relation='RelatedResource', embedded=True)
            ]

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

    def test_format_exception(self):
        exc = RestException('blah blah', status_code=458)
        json_dump, content_type, status_code = SirenAdapter.format_exception(exc)
        data = json.loads(json_dump)
        self.assertEqual(SirenAdapter.formats[0], content_type)
        self.assertEqual(status_code, 458)
        self.assertEqual(data['message'], 'blah blah')

    def test_list_relationship_entity(self):
        """
        Tests a List entity entity
        """
        class Resource(ResourceBase):
            _pks = ['id']
            _relationships = [
                ListRelationship('related', relation='Resource')
            ]
        props = dict(id=1, related=[dict(id=2), dict(id=3)])
        res = Resource(properties=props)
        adapter = SirenAdapter(res)
        entities = adapter.get_entities()
        self.assertEqual(len(entities), 2)

    def test_extra_headers(self):
        adapter = SirenAdapter(None)
        self.assertEqual(adapter.extra_headers, {'Content-Type': 'application/vnd.siren+json'})

    def test_generate_entity_not_all_pks(self):
        class Fake(ResourceBase):
            pks = ('id',)

        f = Fake(properties=dict(val='something'))
        adapter = SirenAdapter(f)
        resp = adapter.generate_entity(f, 'blah', True)
        # Ensure that it is an empty generator
        for r in resp:
            assert False

    def test_generate_fields_for_endpoint_func_empty_no_fields(self):
        """
        Tests that an empty list is returned if
        the fields cannot be found.
        """
        def fake(*args, **kwargs):
            return

        adapter = SirenAdapter(object())
        func_fields = adapter.generate_fields_for_endpoint_funct(fake)
        self.assertListEqual([], func_fields)

    def test_generate_field_for_endpoint_func_url_params(self):
        """
        Tests that url params are not a part of the
        fields returned.
        """
        fields_method = mock.Mock(return_value=[mock.Mock(arg_type=input_categories.URL_PARAMS)])
        endpoint_func = mock.Mock(fields=fields_method)
        adapter = SirenAdapter(mock.MagicMock())
        fields_found = adapter.generate_fields_for_endpoint_funct(endpoint_func)
        self.assertListEqual(fields_found, [])
