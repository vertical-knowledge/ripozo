from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from mock import Mock
from ripozo.dispatch.adapters import BoringJSONAdapter, HalAdapter, SirenAdapter
from ripozo.exceptions import AdapterFormatAlreadyRegisteredException
from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.dispatcher import FakeDispatcher

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
        self.mockKlass.endpoint_dictionary = dict(
            first=[dict(route='/first', methods=['GET'])],
            second=[
                dict(route='/second', methods=['GET'], other='something', andanother='skdfmsdkf'),
                dict(route='/second', methods=['POST'])
            ]
        )

    def tearDown(self):
        self.dispatcher = None

    def test_register_class_routes(self):
        self.dispatcher.register_class_routes(self.mockKlass)
        self.assertDictEqual(self.mockKlass.endpoint_dictionary, self.dispatcher.routes)

    def test_dispatch(self):
        # TODO
        pass

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
