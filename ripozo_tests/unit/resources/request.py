from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import unittest2
from six import StringIO
from werkzeug.test import EnvironBuilder

from ripozo.resources.constants.input_categories import QUERY_ARGS, BODY_ARGS, URL_PARAMS
from ripozo.resources.request import RequestContainer, _parse_query_string, \
    _get_charset, _parse_body, _Headers



class TestRequestContainer(unittest2.TestCase):
    """
    Tests for the RequestContainer
    """

    def dict_helper(self, name):
        d = dict(some='object')
        r = RequestContainer(**{name: d})
        self.assertDictEqual(d, getattr(r, name))
        self.assertNotEqual(id(d), id(getattr(r, name)))

        # Test setting the dict
        d2 = dict(another='object')
        setattr(r, name, d2)
        self.assertNotEqual(d, getattr(r, name))
        self.assertDictEqual(d2, getattr(r, name))
        self.assertNotEqual(id(d2), id(getattr(r, name)))

        # Test empty dict
        r = RequestContainer()
        self.assertIsInstance(getattr(r, name), dict)

    def test_url_params(self):
        self.dict_helper('url_params')

    def test_query_args(self):
        self.dict_helper('query_args')

    def test_body_args(self):
        self.dict_helper('body_args')

    def test_headers(self):
        self.dict_helper('headers')

    def test_content_type(self):
        content_type = 'for real;'
        headers = {'Content-Type': content_type}
        r = RequestContainer(headers=headers)
        self.assertEqual(content_type, r.content_type)
        r = RequestContainer()
        self.assertIsNone(r.content_type)

        # set the content type
        r.content_type = 'blah'
        self.assertEqual(r.content_type, 'blah')

    def test_get(self):
        """
        Tests that the get method appropriately retrieves
        paramaters.
        """
        r = RequestContainer(url_params=dict(key=1, key2=2))
        self.assertEqual(r.get('key'), 1)
        self.assertEqual(r.get('key2'), 2)

        r = RequestContainer(query_args=dict(key=1, key2=2))
        self.assertEqual(r.get('key'), 1)
        self.assertEqual(r.get('key2'), 2)

        r = RequestContainer(body_args=dict(key=1, key2=2))
        self.assertEqual(r.get('key'), 1)
        self.assertEqual(r.get('key2'), 2)

        r = RequestContainer(url_params=dict(key=1), query_args=dict(key=2), body_args=dict(key=3))
        self.assertEqual(r.get('key'), 1)

    def test_get_not_found(self):
        """
        Tests the get with a default value
        """
        r = RequestContainer()
        self.assertEqual(r.get('fake', 'hey'), 'hey')
        self.assertEqual(r.get('fak'), None)

    def test_set_key_error(self):
        """
        Asserts that set raises a key error
        when the value cannot be found.
        """
        req = RequestContainer(query_args=dict(x=1))
        self.assertRaises(KeyError, req.set, 'blah', 'blah')

    def test_set(self):
        """
        Tests the basic set on the request
        without location specified
        """
        original_dict = dict(x=1)
        req = RequestContainer(query_args=original_dict)
        req.set('x', 2)
        self.assertDictEqual(dict(x=2), req.query_args)

        req = RequestContainer(url_params=original_dict)
        req.set('x', 2)
        self.assertDictEqual(dict(x=2), req.url_params)

        req = RequestContainer(body_args=original_dict)
        req.set('x', 2)
        self.assertDictEqual(dict(x=2), req.body_args)

    def test_set_location_specified(self):
        """
        Tests the set on the request container
        with the location specified.
        """
        original_dict = dict(x=1)
        req = RequestContainer(query_args=original_dict)
        req.set('x', 2, QUERY_ARGS)
        self.assertDictEqual(dict(x=2), req.query_args)

        req = RequestContainer(url_params=original_dict)
        req.set('x', 2, URL_PARAMS)
        self.assertDictEqual(dict(x=2), req.url_params)

        req = RequestContainer(body_args=original_dict)
        req.set('x', 2, BODY_ARGS)
        self.assertDictEqual(dict(x=2), req.body_args)

    def test_set_location_specified_new(self):
        """
        Tests the set on the request container
        when the key is not already available and
        the location is specified.
        """
        original_dict = dict(x=1)
        req = RequestContainer(url_params=original_dict)
        req.set('x', 2, QUERY_ARGS)
        self.assertDictEqual(dict(x=2), req.query_args)
        self.assertDictEqual(dict(x=1), req.url_params)

        req = RequestContainer(query_args=original_dict)
        req.set('x', 2, URL_PARAMS)
        self.assertDictEqual(dict(x=2), req.url_params)
        self.assertDictEqual(dict(x=1), req.query_args)

        req = RequestContainer(url_params=original_dict)
        req.set('x', 2, BODY_ARGS)
        self.assertDictEqual(dict(x=2), req.body_args)
        self.assertDictEqual(dict(x=1), req.url_params)

    def test_parse_query_string(self):
        """
        Ensures that the query string is properly parsed
        from the environ object
        """
        query_string = "some=thing&another=else"
        environ = EnvironBuilder(query_string=query_string).get_environ()
        resp = _parse_query_string(environ)
        expected = {
            'some': ['thing'],
            'another': ['else']
        }
        self.assertDictEqual(resp, expected)

    def test_parse_query_string_list(self):
        """Ensure that query string lists are properly parsed"""
        query_string = "field=blah&field=else"
        environ = EnvironBuilder(query_string=query_string).get_environ()
        resp = _parse_query_string(environ)
        expected = {
            'field': [
                'blah',
                'else'
            ]
        }
        self.assertDictEqual(resp, expected)

    def test_parse_body_json(self):
        """Ensure JSON is appropriately loaded"""
        body = {'some': 'thing', 'another': 'thing'}
        body_string = StringIO(json.dumps(body))
        environ = EnvironBuilder(input_stream=body_string).get_environ()
        resp = _parse_body(environ)
        self.assertDictEqual(resp, body)

    def test_parse_body_formencoded(self):
        """Ensure that formencoded data is properly loaded"""
        body = "some=thing&another=else"
        body_string = StringIO(body)
        environ = EnvironBuilder(input_stream=body_string).get_environ()
        resp = _parse_body(environ)

        expected = {
            'some': ['thing'],
            'another': ['else']
        }
        self.assertDictEqual(resp, expected)

    def test_empty_body(self):
        """Ensures an empty body is interpreted as an empty dict"""
        body = ''
        body_string = StringIO(body)
        environ = EnvironBuilder(input_stream=body_string).get_environ()
        resp = _parse_body(environ)
        self.assertDictEqual(resp, {})

    def test_parse_body_none(self):
        """Ensures no body set interpreted as an empty dict"""
        resp = _parse_body({'wsgi.input': None})
        self.assertDictEqual(resp, {})

    def test_parse_body_byte_string(self):
        """Ensure that byte strings can be properly decoded"""
        expected = {"some": ["body"]}
        body_string = b'some=body'
        body = StringIO(body_string)
        environ = EnvironBuilder(input_stream=body).get_environ()

        resp = _parse_body(environ)
        self.assertEqual(resp, expected)

    def test_headers_case_insensitive(self):
        """Ensures the _Headers dict is case insensitive"""
        headers = _Headers()
        expected = 'something'
        headers['first'] = expected
        self.assertEqual(headers['first'], expected)
        self.assertEqual(headers['FIRST'], expected)
        self.assertEqual(headers['First'], expected)
        self.assertEqual(headers['fIrSt'], expected)

        headers['SECOND'] = expected
        self.assertEqual(headers['second'], expected)
        self.assertEqual(headers['SECOND'], expected)
        self.assertEqual(headers['Second'], expected)
        self.assertEqual(headers['sEcOnD'], expected)

    def test_headers_from_wsgi_environ_not_headers(self):
        """Ensure that wsgi environ keys are rejected appropriately"""
        fake_headers = {
            'notaheader': 'first',
            'NOTAHEADER': 'blah',
            'HTTPNOTAHEADER': 'blah',
            'http_notaheader': 'blah'
        }

        headers_dict_fake = _Headers.from_wsgi_environ(fake_headers)
        self.assertEqual(len(headers_dict_fake), 0)

    def test_headers_from_wsgi_environ_real_headers(self):
        """Ensure real headers are appropriately retrieved"""
        real_headers = {
            'HTTP_SOME_HEADER': 'blah',
            'CONTENT_TYPE': 'blah',
            'CONTENT_LENGTH': 'blah',
            'HTTP_ANOTHER_HEADER': 'blah'
        }

        expected = {
            'Some-Header': 'blah',
            'Content-Type': 'blah',
            'Content-Length': 'blah',
            'Another-Header': 'blah'
        }

        headers_dict_real = _Headers.from_wsgi_environ(real_headers)
        self.assertEqual(len(headers_dict_real), len(real_headers))
        self.assertDictEqual(expected, headers_dict_real)

    def test_from_wsgi_environ(self):
        """Test creating a RequestContainer from a wsgi environ"""
        expected_body = {'something': 'thing'}
        body = StringIO(json.dumps(expected_body))
        headers = {
            'Content-Type': 'something',
            'Some-Other-Header': 'blah'
        }
        environ_builder = EnvironBuilder(query_string='some=thing',
                                         method='FAKE',
                                         input_stream=body,
                                         headers=headers)
        environ = environ_builder.get_environ()

        url_params = {'id': 1}
        resp = RequestContainer.from_wsgi_environ(environ, url_params)

        self.assertIsInstance(resp, RequestContainer)
        self.assertDictContainsSubset(headers, resp.headers)
        self.assertDictEqual(expected_body, resp.body_args)
        self.assertEqual(resp.query_args, {'some': ['thing']})
        self.assertEqual(resp.method, 'FAKE')
        self.assertDictEqual(environ, resp.environ)

    def test_get_charset(self):
        """Test getting the charset from the environ"""
        headers = {'Content-Type': 'text/plain; charset=blah'}
        environ = EnvironBuilder(headers=headers).get_environ()
        charset = _get_charset(environ)
        self.assertEqual(charset, 'blah')

    def test_get_charset_byte_header(self):
        """Test getting the charset when the headers are bytes"""
        environ = {b'CONTENT_TYPE': b'text/plain; charset=blah'}
        charset = _get_charset(environ)
        self.assertEqual(charset, 'blah')
