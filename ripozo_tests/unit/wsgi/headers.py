from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
import unittest2

from ripozo.wsgi.headers import Headers, get_raw_content_type


class TestHeaders(unittest2.TestCase):
    def test_headers_case_insensitive(self):
        """Ensures the _Headers dict is case insensitive"""
        headers = Headers()
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

        headers_dict_fake = Headers.from_wsgi_environ(fake_headers)
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

        headers_dict_real = Headers.from_wsgi_environ(real_headers)
        self.assertEqual(len(headers_dict_real), len(real_headers))
        self.assertDictEqual(expected, headers_dict_real)



class TestGetRawContentType(unittest2.TestCase):
    def test_get_content_type_unicode(self):
        expected = 'application/json'
        environ = {'CONTENT_TYPE': expected}
        resp = get_raw_content_type(environ)
        self.assertEqual(expected, resp)
        self.assertIsInstance(resp, six.text_type)

    def test_get_content_type_bytes(self):
        expected = 'application/json'
        environ = {'CONTENT_TYPE': expected.encode('latin1')}
        resp = get_raw_content_type(environ)
        self.assertEqual(expected, resp)
        self.assertIsInstance(resp, six.text_type)

    def test_get_content_type_no_content_type(self):
        resp = get_raw_content_type({})
        self.assertEqual('', resp)
