from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import apimethod, translate

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
            return mock.MagicMock()

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

    def test_preprocessors_and_postprocessors(self):
        pre1 = mock.MagicMock()
        pre2 = mock.MagicMock()
        post1 = mock.MagicMock()
        post2 = mock.MagicMock()

        class Blah(object):
            preprocessors = [pre1, pre2]
            postprocessors = [post1, post2]

            @apimethod()
            def fake(cls, *args, **kwargs):
                return mock.MagicMock()

        Blah.fake(None)
        self.assertEqual(pre1.call_count, 1)
        self.assertEqual(pre2.call_count, 1)
        self.assertEqual(post1.call_count, 1)
        self.assertEqual(post2.call_count, 1)

    def test_translate(self):
        mkc = mock.MagicMock()

        @translate(fields=[1, 2])
        def fake(*args, **kwargs):
            return mkc()

        self.assertIsInstance(fake.fields, list)
        self.assertListEqual(fake.fields, [1, 2])

        request = mock.Mock()
        x = fake(1, request)
        self.assertEqual(mkc.call_count, 1)
        self.assertEqual(request.translate.call_count, 1)


