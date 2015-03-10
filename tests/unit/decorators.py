from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import apimethod

from ripozo_tests.python2base import TestBase

import mock
import unittest


class TestApiMethodDecorator(TestBase, unittest.TestCase):
    def test_init(self):
        route = 'something'
        endpoint = 'endpoint'
        api = apimethod(route=route, endpoint=endpoint, another=True, and_another=False)
        self.assertEqual(route, api.route)
        self.assertEqual(endpoint, api.endpoint)
        self.assertDictEqual(dict(another=True, and_another=False), api.options)

    def test_call(self):
        route = 'something'
        endpoint = 'endpoint'

        def fake(*args, **kwargs):
            pass

        api = apimethod(route=route, endpoint=endpoint)
        wrapped = api(fake)
        self.assertTrue(getattr(wrapped, 'rest_route', False))
        routes = getattr(wrapped, 'routes')
        self.assertIsInstance(routes, list)
        self.assertEqual(len(routes), 1)
        self.assertEqual((route, endpoint, {}), routes[0])
        api2 = apimethod(route='another', endpoint='thing')

        wrapped = api2(wrapped)
        routes = getattr(wrapped, 'routes')
        self.assertEqual(len(routes), 2)
        self.assertEqual(('another', 'thing', {}), routes[1])
