from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from mock import Mock
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
        pass
