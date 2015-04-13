from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from mock import Mock, MagicMock

from ripozo.dispatch.adapters import BoringJSONAdapter, HalAdapter, SirenAdapter
from ripozo.decorators import apimethod
from ripozo.exceptions import AdapterFormatAlreadyRegisteredException
from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.dispatcher import FakeDispatcher

import mock
import unittest


class TestDispatchBase(TestBase, unittest.TestCase):
    """
    This class is responsible for testing
    the reusable portions of the dispatcher
    that are availabl in the dispatch.dispatch_base.py
    file
    """
    def setUp(self):
        self.dispatcher = FakeDispatcher()
        self.mockKlass = Mock()

        self.mockKlass.endpoint_dictionary = Mock(return_value=dict(
            first=[dict(route='/first', methods=['GET'])],
            second=[
                dict(route='/second', methods=['GET'], other='something', andanother='skdfmsdkf'),
                dict(route='/second', methods=['POST'])
            ]
        ))
        self.mockKlass.__name__ = 'mockKlass'

    def tearDown(self):
        self.dispatcher = None

    def test_dispatch(self):
        endpoint_func = MagicMock()
        self.assertRaises(TypeError, self.dispatcher.dispatch, endpoint_func, 'fake')
        self.assertEqual(endpoint_func.call_count, 1)
        adapter = MagicMock()
        adapter.formats = ['fake']
        self.dispatcher.register_adapters(adapter)
        self.dispatcher.dispatch(endpoint_func, 'fake')
        self.assertEqual(adapter.call_count, 1)
        self.assertEqual(endpoint_func.call_count, 2)

    def test_register_adapters(self):
        """Tests whether adapters are properly registered"""
        adapters = (SirenAdapter, HalAdapter, BoringJSONAdapter,)
        self.dispatcher.register_adapters(*adapters)
        self.assertEqual(self.dispatcher.default_adapter, SirenAdapter)
        for adapter in adapters:
            for format in adapter.formats:
                self.assertIn(format, self.dispatcher.adapter_formats)
                self.assertEqual(adapter, self.dispatcher.adapter_formats[format])

    def test_overriding_adapters(self):
        """Tests whether overriding adapters raises an exception"""
        adapters = (SirenAdapter, HalAdapter)
        self.dispatcher.register_adapters(*adapters)

        # This will have the same formats as the SirenAdapter
        class TempAdapter(SirenAdapter):
            pass

        self.assertRaises(AdapterFormatAlreadyRegisteredException, self.dispatcher.register_adapters, TempAdapter)

    @mock.patch.object(FakeDispatcher, 'register_route')
    def test_register_class_routes(self, mck):
        """
        Tests whether the ``AdapterBase().register_class_routes`` method
        properly call the ``AdapterBase().register_route`` method
        """
        self.dispatcher.register_class_routes(self.mockKlass)
        self.assertEqual(mck.call_count, 3)

    @mock.patch.object(FakeDispatcher, 'register_route')
    def test_register_mutiple_resource_classes(self, mck):
        mockKlass = Mock()
        mockKlass.endpoint_dictionary = Mock(return_value=dict(
            first=[dict(route='/2/first', methods=['GET'])],
            second=[
                dict(route='/2/second', methods=['GET'], other='something', andanother='skdfmsdkf'),
            ]
        ))
        mockKlass.__name__ = 'mockKlass2'
        self.dispatcher.register_resources(mockKlass, self.mockKlass)

        self.assertEqual(mck.call_count, 5)