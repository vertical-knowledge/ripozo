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


class TestConstructRequestHelper(object):
    def construct_request_from_wsgi_environ(self, adapter_class):
        expected_body = {'first': 'something'}
        query_string = {'second': 'another'}
        body = StringIO(json.dumps(expected_body))
        query_string = urllib.parse.urlencode(query_string)
        expected_query_string = {'second': ['another']}
        expected_method = 'BLAH'
        headers = {'Some-Header': 'blah'}
        environ = EnvironBuilder(headers=headers, input_stream=body,
                                 query_string=query_string, method=expected_method).get_environ()
        expected_url_params = {'blah': 'blah'}
        request = adapter_class.construct_request_from_wsgi_environ(environ, expected_url_params)

        self.assertDictEqual(expected_body, request.body_args)
        self.assertDictEqual(expected_query_string, request.query_args)
        self.assertEqual(expected_method, request.method)
        for key, value in six.iteritems(headers):
            self.assertEqual(value, request.headers[key])
        self.assertDictEqual(expected_url_params, request.url_params)
