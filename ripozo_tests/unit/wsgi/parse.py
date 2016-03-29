# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import warnings

import six
import unittest2
from six import StringIO, BytesIO
from six.moves import urllib
from werkzeug.test import EnvironBuilder

from ripozo.exceptions import UnreadableBodyException
from ripozo.wsgi.parse import coerce_body_to_unicode, json_loads_backwards_compatible, \
    parse_form_encoded, _get_charset, _parse_query_string, get_http_verb, \
    construct_request_from_wsgi_environ


class TestParseFormEncoded(unittest2.TestCase):

    def test_parse_form_encoded_bytes_to_unicode(self):
        """
        Simple version starting bytes ending unicode
        """
        query_dict = {b'some': b'another', b'and': b'another'}
        query_string = urllib.parse.urlencode(query_dict)

        resp = parse_form_encoded(query_string)
        expected = {u'some': [u'another'], u'and': [u'another']}
        self.assertDictEqual(expected, resp)
        self.assert_form_encoded_unicode(resp)

    def test_empty_body(self):
        """Ensures an empty body is interpreted as an empty dict"""
        body = ''
        resp = parse_form_encoded(body)
        self.assertDictEqual(resp, {})

    def test_unparseable_body(self):
        """Ensure deprecation warnings are raised"""
        body = "&&;;&"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            resp = parse_form_encoded(body)
            self.assertEqual(len(w), 1)
            self.assertIsInstance(w[0].message, DeprecationWarning)
        self.assertDictEqual(resp, {})

    def test_parse_form_encoded_unicode_to_unicode(self):
        """
        Version where the query string is unicode
        """
        query_dict = {u'some': u'another', u'and': u'another'}
        query_string = urllib.parse.urlencode(query_dict)

        resp = parse_form_encoded(query_string)
        expected = {u'some': [u'another'], u'and': [u'another']}
        self.assertDictEqual(expected, resp)
        self.assert_form_encoded_unicode(resp)

    def test_parse_form_encoded_special_characters_bytes(self):
        """
        Tests passing in special character bytes
        """
        query_dict = {
            u'søµ´'.encode('utf-8'): u'å˜†˙´'.encode('utf-8'),
            u'å˜'.encode('utf-8'): 'å˜†˙´'.encode('utf-8')
        }
        query_string = urllib.parse.urlencode(query_dict)

        resp = parse_form_encoded(query_string)
        expected = {u'søµ´': [u'å˜†˙´'], u'å˜': [u'å˜†˙´']}
        self.assertDictEqual(expected, resp)
        self.assert_form_encoded_unicode(resp)

    def assert_form_encoded_unicode(self, dictionary):
        """
        Ensure all keys and values are unicode
        """
        for key, value in dictionary.items():
            self.assertIsInstance(key, six.text_type)
            for val in value:
                self.assertIsInstance(val, six.text_type)


class TestCoerceBodyToUnicode(unittest2.TestCase):
    """
    Contains the various tests for the
    coerce_body_to_unicode function
    """
    def test_empty_wsgi_input(self):
        """Ensure empty string returned"""
        expected = ''
        resp = coerce_body_to_unicode({})
        self.assertEqual(expected, resp)

    def test_text_type_body(self):
        expected = u'blah blah'
        body = StringIO(expected)
        environ = EnvironBuilder(input_stream=body).get_environ()
        resp = coerce_body_to_unicode(environ)
        self.assertIsInstance(resp, six.text_type)
        self.assertEqual(expected, resp)

    def test_bytes_body_valid_charset(self):
        expected = 'blah blah'
        encoding_type = 'cp950'
        content_type = 'text/plain; charset={0}'.format(encoding_type)
        raw_text = expected.encode(encoding_type)
        body = BytesIO(raw_text)
        environ = EnvironBuilder(input_stream=body, content_type=content_type).get_environ()
        resp = coerce_body_to_unicode(environ)
        self.assertIsInstance(resp, six.text_type)
        self.assertEqual(expected, resp)

    def test_bytes_body_invalid_charset(self):
        expected = '∫¬å˙∫…å˙'
        encoding_type = 'cp950'

        content_type = 'text/plain; charset={0}'.format('ascii')
        raw_text = expected.encode('utf-8')
        body = BytesIO(raw_text)
        environ = EnvironBuilder(input_stream=body, content_type=content_type).get_environ()

        self.assertRaises(UnreadableBodyException, coerce_body_to_unicode, environ)

    def test_bytes_body_bad_encoding_type(self):
        expected = 'blah blah'
        raw_text = expected.encode('cp950')
        body = BytesIO(raw_text)
        content_type = 'text/plain; charset={0}'.format('notreal')
        environ = EnvironBuilder(input_stream=body, content_type=content_type).get_environ()

        self.assertRaises(UnreadableBodyException, coerce_body_to_unicode, environ)


class TestJsonLoadsBackwardsCompatible(unittest2.TestCase):
    def test_empty_body_returns_empty_dict(self):
        expected = {}
        resp = json_loads_backwards_compatible('', 'application/json')
        self.assertDictEqual(expected, resp)

        resp = json_loads_backwards_compatible(None, 'application/json')
        self.assertDictEqual(expected, resp)

    def test_json_body_valid(self):
        expected = {'first': 'value', 'second': 'blah'}
        raw = json.dumps(expected)
        resp = json_loads_backwards_compatible(raw, 'application/json')
        self.assertDictEqual(expected, resp)

    def test_form_encoded_ensure_warning(self):
        original = {'first': 'value', 'second': 'blah'}
        expected = {'first': ['value'], 'second': ['blah']}
        raw = urllib.parse.urlencode(original)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            resp = json_loads_backwards_compatible(raw, 'application/json')
            self.assertEqual(len(w), 1)
            self.assertIsInstance(w[0].message, DeprecationWarning)
        self.assertDictEqual(expected, resp)


class TestGetCharset(unittest2.TestCase):

    def test_get_charset(self):
        """Test getting the charset from the environ"""
        headers = {'Content-Type': 'text/plain; charset=blah'}
        environ = EnvironBuilder(headers=headers).get_environ()
        charset = _get_charset(environ)
        self.assertEqual(charset, 'blah')

    def test_get_charset_byte_header(self):
        """Test getting the charset when the headers are bytes"""
        environ = {'CONTENT_TYPE': b'text/plain; charset=blah'}
        charset = _get_charset(environ)
        self.assertEqual(charset, 'blah')


class TestParseQueryString(unittest2.TestCase):
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


class TestGetHttpVerb(unittest2.TestCase):
    def test_unicode_request_method(self):
        environ = {'REQUEST_METHOD': 'blah'}
        method = get_http_verb(environ)
        self.assertEqual("BLAH", method)
        self.assertIsInstance(method, six.text_type)

    def test_bytes_request_method(self):
        environ = {'REQUEST_METHOD': b'blah'}
        method = get_http_verb(environ)
        self.assertEqual("BLAH", method)
        self.assertIsInstance(method, six.text_type)

    def test_no_request_method_expect_exception(self):
        self.assertRaises(KeyError, get_http_verb, {})
