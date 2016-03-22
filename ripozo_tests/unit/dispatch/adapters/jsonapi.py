from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import six
import unittest2
from six import StringIO
from six.moves import urllib
from werkzeug.test import EnvironBuilder

from ripozo import ResourceBase, Relationship, RequestContainer, ListRelationship
from ripozo.adapters.jsonapi import JSONAPIAdapter
from ripozo.exceptions import JSONAPIFormatException, RestException


class TestJSONAPIAdapter(unittest2.TestCase):
    def test_construct_pks_no_pks(self):
        """When there are no ids"""
        class MyResource(ResourceBase):
            pks = tuple()

        response = JSONAPIAdapter._construct_id(MyResource())
        self.assertEqual(response, '')

    def test_construct_pks_one_pk(self):
        """Constructing a single id"""
        class MyResource(ResourceBase):
            pks = 'id',

        response = JSONAPIAdapter._construct_id(MyResource(properties=dict(id=1)))
        self.assertEqual(response, '1')

    def test_construct_pks_multiple_pks(self):
        """Constructing a single id from multiple"""
        class MyResource(ResourceBase):
            pks = 'id', 'pk'

        response = JSONAPIAdapter._construct_id(MyResource(properties=dict(id=1, pk=2)))
        self.assertEqual(response, '1/2')

    def test_construct_data_with_base_url(self):
        """Tests when there is a base_url"""
        class MyResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(id=1, field='value'))
        adapter = JSONAPIAdapter(resource=res, base_url='http://blah.com')
        resp = adapter._construct_data(res)
        self.assertEqual(resp['links']['self'], 'http://blah.com/my_resource/1')

    def test_construct_data_embedded(self):
        """Ensures that reltionships, links, and attributes are included"""
        class MyResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(id=1, field='value'))
        adapter = JSONAPIAdapter(resource=res)
        resp = adapter._construct_data(res, embedded=True)
        self.assertDictEqual(resp['relationships'], dict())
        self.assertDictEqual(resp['attributes'], res.properties)
        self.assertDictEqual(dict(self='/my_resource/1'), resp['links'])
        self.assertEqual('1', resp['id'])
        self.assertEqual('my_resource', resp['type'])

    def test_construct_data_not_embedded(self):
        """Only the self link should be included"""
        class MyResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(id=1, field='value'))
        adapter = JSONAPIAdapter(resource=res)
        resp = adapter._construct_data(res, embedded=False)
        self.assertNotIn('relationships', resp)
        self.assertNotIn('attributes', resp)
        self.assertDictEqual(dict(self='/my_resource/1'), resp['links'])
        self.assertEqual('1', resp['id'])
        self.assertEqual('my_resource', resp['type'])

    def test_construct_links_no_links(self):
        """Constructing links when there are not any"""
        class MyResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(id=1, field='value'))
        adapter = JSONAPIAdapter(resource=res)
        resp = adapter._construct_links(res)
        self.assertDictEqual(dict(self='/my_resource/1'), resp)

    def test_construct_links(self):
        """Expected case"""
        class MyResource(ResourceBase):
            pks = 'id',
            _links = Relationship('child', property_map=dict(child_id='pk'), relation='RelatedResource'),

        class RelatedResource(ResourceBase):
            pks = 'pk',

        res = MyResource(properties=dict(id=1), meta=dict(links=dict(child_id=2)))
        adapter = JSONAPIAdapter(resource=res)
        resp = adapter._construct_links(res)
        expected = dict(self='/my_resource/1', child='/related_resource/2')
        self.assertEqual(resp, expected)

    def test_format_request(self):
        """Expected case"""
        req = RequestContainer(body_args=dict(data=dict(attributes=dict(id=1))))
        resp = JSONAPIAdapter.format_request(req)
        self.assertDictEqual(resp.body_args, dict(id=1))

    def test_format_request_improper_request(self):
        """
        Ensures that the appropriate exception is raised when
        the request is improperly formatted
        """
        req = RequestContainer(body_args=dict(id=1))
        self.assertRaises(JSONAPIFormatException, JSONAPIAdapter.format_request, req)
        req = RequestContainer(body_args=dict(data=dict(id=1)))
        self.assertRaises(JSONAPIFormatException, JSONAPIAdapter.format_request, req)

    def test_format_request_relationships(self):
        """
        Tests that relationships are appropriately reformatted
        to the ripozo style.
        """
        class RelatedResource(ResourceBase):
            pks = ('id', 'pk',)

        rel_dict = {'resource': dict(data=dict(id='1/2', type='related_resource'))}
        req = RequestContainer(body_args=dict(data=dict(attributes=dict(id=1), relationships=rel_dict)))
        resp = JSONAPIAdapter.format_request(req)
        self.assertDictEqual(resp.body_args, {'id': 1, 'resource.id': '1', 'resource.pk': '2'})

    def test_format_request_relationship_bad_format(self):
        """Ensures exception is raised when an inappropriate relation format is presented"""
        class RelatedResource(ResourceBase):
            pks = ('id', 'pk',)

        rel_dict = {'resource': dict(data=dict(type='related_resource'))}
        req = RequestContainer(body_args=dict(data=dict(attributes=dict(id=1), relationships=rel_dict)))
        self.assertRaises(JSONAPIFormatException, JSONAPIAdapter.format_request, req)

        rel_dict = {'resource': dict(data=dict(id='1/2'))}
        req = RequestContainer(body_args=dict(data=dict(attributes=dict(id=1), relationships=rel_dict)))
        self.assertRaises(JSONAPIFormatException, JSONAPIAdapter.format_request, req)

        rel_dict = {'resource': dict(id='1/2', type='related_resource')}
        req = RequestContainer(body_args=dict(data=dict(attributes=dict(id=1), relationships=rel_dict)))
        self.assertRaises(JSONAPIFormatException, JSONAPIAdapter.format_request, req)

    def test_parse_id_invalid_type(self):
        """Asserts exception raised when resource_name is not valid"""
        self.assertRaises(JSONAPIFormatException, JSONAPIAdapter._parse_id, 'id', 'fake_resource')

    def test_parse_id_inappropriate_id(self):
        """Asserts exception raised when pks length does not match the ids"""
        class MyResource(ResourceBase):
            pks = 'pk', 'id', 'id2',

        id_ = '1/2'
        self.assertRaises(JSONAPIFormatException, JSONAPIAdapter._parse_id, id_, 'my_resource')

    def test_parse_id(self):
        """Normal case"""
        class MyResource(ResourceBase):
            pks = 'pk', 'id',

        id_ = '1/2'
        resp = JSONAPIAdapter._parse_id(id_, 'my_resource')
        self.assertDictEqual(dict(pk='1', id='2'), resp)

    def test_format_exception_ripozo_exception(self):
        """Ensures that the appropriate status code is returned"""
        exc = RestException('some message', status_code=654)
        body, content_type, status_code = JSONAPIAdapter.format_exception(exc)
        body = json.loads(body)
        expected = dict(
            errors=[
                dict(status=654, title='RestException', detail='some message')
            ]
        )
        self.assertDictEqual(expected, body)
        self.assertEqual(content_type, 'application/vnd.api+json')
        self.assertEqual(status_code, 654)

    def test_format_exception(self):
        """For when a non ripozo exception is passed in"""
        exc = Exception('some message')
        body, content_type, status_code = JSONAPIAdapter.format_exception(exc)
        body = json.loads(body)
        expected = dict(
            errors=[
                dict(status=500, title='Exception', detail='some message')
            ]
        )
        self.assertDictEqual(expected, body)
        self.assertEqual(content_type, 'application/vnd.api+json')
        self.assertEqual(status_code, 500)

    def test_construct_relationship(self):
        """Single relationship"""
        class MyResource(ResourceBase):
            _relationships = Relationship('related', relation='RelatedResource'),

        class RelatedResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(related=dict(id=1)))
        adapter = JSONAPIAdapter(res, base_url='/blah')
        resp = adapter._construct_relationships(res)
        self.assertIn('related', resp)
        self.assertIn('data', resp['related'])
        data = resp['related']['data']
        self.assertEqual(len(data), 1)
        data = data[0]
        self.assertDictEqual(dict(type='related_resource', id='1',
                                  links=dict(self='/blah/related_resource/1')), data)

    def test_construct_relationship_list(self):
        """A ListRelationship instance"""
        class MyResource(ResourceBase):
            _relationships = ListRelationship('related', relation='RelatedResource'),

        class RelatedResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(related=[dict(id=2), dict(id=1)]))
        adapter = JSONAPIAdapter(res, base_url='/blah')
        resp = adapter._construct_relationships(res)
        self.assertIn('related', resp)
        self.assertIn('data', resp['related'])
        data = resp['related']['data']
        self.assertEqual(len(data), 2)
        for related in data:
            self.assertEqual(related['type'], 'related_resource')
            self.assertTrue(related['links']['self'].startswith('/blah/related_resource'))

    def test_construct_relationship_embedded(self):
        """An embedded relationship"""
        class MyResource(ResourceBase):
            _relationships = Relationship('related', relation='RelatedResource', embedded=True),

        class RelatedResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(related=dict(id=1, value=2)))
        adapter = JSONAPIAdapter(res, base_url='/blah')
        resp = adapter._construct_relationships(res)
        self.assertIn('related', resp)
        self.assertIn('data', resp['related'])
        data = resp['related']['data']
        self.assertEqual(len(data), 1)
        data = data[0]
        self.assertIn('attributes', data)
        self.assertDictEqual(
            dict(
                type='related_resource', id='1',
                links=dict(self='/blah/related_resource/1'),
                relationships={}, attributes=dict(id=1, value=2)
            ), data)

    def test_formatted_body(self):
        """Simple explosion test"""
        class MyResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(id=1))
        adapter = JSONAPIAdapter(res)
        resp = adapter.formatted_body
        body = json.loads(resp)
        self.assertIn('data', body)
        body = body['data']
        self.assertEqual(body['id'], '1')
        self.assertEqual(body['type'], 'my_resource')
        self.assertDictEqual(body['links'], dict(self='/my_resource/1'))
        self.assertDictEqual(body['attributes'], dict(id=1))

    def test_no_pks_resource_construct_id(self):
        """
        Tests that a response is appropriately returned
        if there are no pks
        """
        class MyResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(value=1), no_pks=True)
        id_ = JSONAPIAdapter._construct_id(res)
        self.assertEqual(id_, "")

    def test_no_pks_resource(self):
        """
        Tests that a resource with no pks is appropriately
        constructed.
        """
        class MyResource(ResourceBase):
            pks = 'id',

        res = MyResource(properties=dict(value=1), no_pks=True)
        adapter = JSONAPIAdapter(res)
        resp = adapter.formatted_body
        data = json.loads(resp)['data']
        self.assertDictEqual(data['attributes'], dict(value=1))
        self.assertEqual(data['links'], dict(self='/my_resource'))
        self.assertEqual(data['id'], '')
        self.assertEqual(data['type'], 'my_resource')

    def test_construct_request_from_wsgi_environ(self):
        expected_body = {'first': 'something'}
        query_string = {'second': 'another'}
        actual_body = dict(data=dict(attributes=expected_body))
        body = StringIO(json.dumps(actual_body))
        query_string = urllib.parse.urlencode(query_string)
        expected_query_string = {'second': ['another']}
        expected_method = 'BLAH'
        headers = {'Some-Header': 'blah'}
        environ = EnvironBuilder(headers=headers, input_stream=body,
                                 query_string=query_string, method=expected_method).get_environ()
        expected_url_params = {'blah': 'blah'}
        request = JSONAPIAdapter.construct_request_from_wsgi_environ(environ, expected_url_params)

        self.assertDictEqual(expected_body, request.body_args)
        self.assertDictEqual(expected_query_string, request.query_args)
        self.assertEqual(expected_method, request.method)
        for key, value in six.iteritems(headers):
            self.assertEqual(value, request.headers[key])
        self.assertDictEqual(expected_url_params, request.url_params)
