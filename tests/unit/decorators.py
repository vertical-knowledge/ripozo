from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import apimethod, translate, _apiclassmethod, classproperty
from ripozo.exceptions import TranslationException, ValidationException
from ripozo.viewsets.fields.common import IntegerField
from ripozo.viewsets.request import RequestContainer
from ripozo.viewsets.resource_base import ResourceBase

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
        self.assertTrue(getattr(wrapped, '__rest_route__', False))
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
        fields = [1, 2]

        @translate(fields=fields)
        def fake(*args, **kwargs):
            return mkc()

        self.assertIsInstance(fake.fields(None), list)
        self.assertListEqual(fake.fields(None), [1, 2])

        request = mock.Mock()
        x = fake(mock.MagicMock(), request)
        self.assertEqual(mkc.call_count, 1)
        self.assertEqual(request.translate.call_count, 1)
        x = request.translate.call_args_list
        self.assertListEqual(x[0][0][0], fields)

    def test_wrapping_apimethod(self):
        """
        Tests wrapping an apimethod and calling it.

        This is primarily due to the failure when a
        descriptor is wrapped (i.e. like in the classmethod
        decorator).
        """
        mck = mock.MagicMock()

        class MyFakeResource(ResourceBase):
            @translate(fields=[1, 2])
            @apimethod(methods=['GET'])
            def fake(*args, **kwargs):
                return mck

        rsp = MyFakeResource.fake(mock.MagicMock())
        self.assertEqual(rsp, mck)
        self.assertEqual([('', None, dict(methods=['GET']),)], MyFakeResource.fake.routes)

    def test_calling_apiclassmethod(self):
        """
        Tests the the _apiclassmethod decorator works
        as intended.
        """
        class MyClass(object):
            @_apiclassmethod
            def fake(cls):
                return cls
        self.assertEqual(MyClass.fake(), MyClass)

    def test_nested_apiclassmethod(self):
        """
        Tests that the _apiclassmethod decorator works
        when wrapped twice.
        """
        class MyClass(object):
            @_apiclassmethod
            @_apiclassmethod
            def fake(cls):
                return cls

        self.assertEqual(MyClass.fake(), MyClass)

    def test_calling_apiclassmethod_on_instance(self):
        """
        Tests that an _apiclassmethod decorator still
        works on an instance rather than a class.
        """
        class MyClass(object):
            @_apiclassmethod
            def fake(cls):
                return cls
        self.assertEqual(MyClass().fake(), MyClass)

    def test_nested_apiclassmethod_on_instance(self):
        """
        Tests that a nested _apiclassmethod decorator
        works on an instance even when nested.
        """
        class MyClass(object):
            @_apiclassmethod
            @_apiclassmethod
            def fake(cls):
                return cls

        self.assertEqual(MyClass().fake(), MyClass)

    def test_call_nested_apiclassmethod(self):
        """
        Tests that a nested apiclassmethod is still callable
        """
        class MyClass(object):
            @_apiclassmethod
            @_apiclassmethod
            def fake(cls, first, second):
                return cls, first, second
        first = 1
        second = 2
        response = MyClass.fake(first, second)
        self.assertEqual(response[0], MyClass)
        self.assertEqual(response[1], first)
        self.assertEqual(response[2], second)

    def test_apiclassmethod_func_name(self):
        """
        Tests that the _apiclassmethod appropriately
        gets the func_name
        """
        class MyClass(object):
            @_apiclassmethod
            def fake(cls, first, second):
                return cls, first, second
        self.assertEqual(MyClass.fake.func_name, 'fake')

    def test_nested_apiclassmethod_funcname(self):
        """
        Tests that a nested _apiclassmethod appropriately
        returns the function name
        """
        class MyClass(object):
            @_apiclassmethod
            @_apiclassmethod
            def fake(cls, first, second):
                return cls, first, second
        self.assertEqual(MyClass.fake.func_name, 'fake')

        class OtherClass(object):
            def fake2(cls, req):
                return cls, req
        method = _apiclassmethod(OtherClass.fake2)
        method = _apiclassmethod(method)
        self.assertEqual(method.__name__, 'fake2')
        self.assertEqual(method.__name__, method.func_name)

    def test_multiple_apimethods(self):
        """
        Tests that multiple apimethod decorators work
        """
        class MyClass(ResourceBase):
            @apimethod(route='something', methods=['GET'])
            @apimethod(route='another', methods=['GET'])
            def fake(cls, request):
                return cls, request

        self.assertEqual(len(MyClass.fake.routes), 2)
        self.assertIsRestRoute(MyClass.fake)

    def assertIsRestRoute(self, method):
        is_rest_route = getattr(method, 'rest_route', False) or getattr(method, '__rest_route__', False)
        self.assertTrue(is_rest_route)

    def test_class_property(self):
        class Fake(object):
            x = 'hi'

            @classproperty
            def hello(cls):
                return cls.x

        self.assertEqual(Fake.hello, 'hi')
        Fake.x = 'another'
        self.assertEqual(Fake.hello, 'another')

        f = Fake()
        self.assertEqual(f.hello, 'another')
        self.assertEqual(getattr(f, 'hello'), 'another')
        self.assertEqual(getattr(Fake, 'hello'), 'another')

    def test_translate_failure(self):
        """
        Tests whether the translate decorator appropriately
        calls translate when validate=False
        """
        class TranslateClass(ResourceBase):
            @apimethod(methods=['GET'])
            @translate(fields=[IntegerField('id', required=True)], validate=False)
            def hey(cls, req):
                return

        req = RequestContainer(body_args=dict(id='notvalid'))
        self.assertRaises(TranslationException, TranslateClass.hey, req)

    def test_translate_success(self):
        """
        Tests that the translate decorator will succesfully
        translate a parameter
        """
        class TranslateClass2(ResourceBase):
            @apimethod(methods=['GET'])
            @translate(fields=[IntegerField('id', required=True)], validate=False)
            def hey(cls, req):
                return req.body_args.get('id')

        req = RequestContainer(body_args=dict(id='10'))
        id = TranslateClass2.hey(req)
        self.assertIsInstance(id, int)

    def test_apimethod_and_translate_endpoints(self):
        class Fake(ResourceBase):
            @apimethod(methods=['GET'])
            @translate(fields=[])
            def fake(cls, *args, **kwargs):
                return cls, args, kwargs

        self.assertEqual(len(Fake.endpoint_dictionary()), 1)