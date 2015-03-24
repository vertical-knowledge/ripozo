from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.constructor import ResourceMetaClass
from ripozo.viewsets.restmixins import Create, Retrieve, Update, Delete, RetrieveUpdateDelete, \
    RetrieveUpdate, CreateRetrieveList, RetrieveList

from ripozo_tests.python2base import TestBase

import mock
import unittest


class TestMixins(TestBase, unittest.TestCase):

    def setUp(self):
        ResourceMetaClass.registered_names_map = {}
        ResourceMetaClass.registered_resource_classes = {}

    def test_create(self):
        manager2 = mock.MagicMock()

        class T1(Create):
            manager = manager2

        request = mock.MagicMock()
        response = T1.create(request)
        self.assertEqual(request.translate.call_count, 1)
        self.assertEqual(manager2.create.call_count, 1)
        self.assertIsInstance(response, T1)

    def test_retrieve_list(self):
        manager2 = mock.MagicMock()
        manager2.retrieve_list = mock.MagicMock(return_value=(mock.MagicMock(), mock.MagicMock()))

        class T1(RetrieveList):
            manager = manager2

        request = mock.MagicMock()
        response = T1.retrieve_list(request)
        self.assertEqual(manager2.retrieve_list.call_count, 1)
        self.assertIsInstance(response, T1)

    def test_retrieve(self):
        manager2 = mock.MagicMock()

        class T1(Retrieve):
            manager = manager2

        request = mock.MagicMock()
        response = T1.retrieve(request)
        self.assertEqual(request.translate.call_count, 1)
        self.assertEqual(manager2.retrieve.call_count, 1)
        self.assertIsInstance(response, T1)

    def test_update(self):
        manager2 = mock.MagicMock()

        class T1(Update):
            manager = manager2

        request = mock.MagicMock()
        response = T1.update(request)
        self.assertEqual(request.translate.call_count, 1)
        self.assertEqual(manager2.update.call_count, 1)
        self.assertIsInstance(response, T1)

    def test_delete(self):
        manager2 = mock.MagicMock()

        class T1(Delete):
            manager = manager2

        request = mock.MagicMock()
        response = T1.delete(request)
        self.assertEqual(request.translate.call_count, 1)
        self.assertEqual(manager2.delete.call_count, 1)
        self.assertIsInstance(response, T1)
