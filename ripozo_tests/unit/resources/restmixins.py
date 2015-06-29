from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo import ResourceBase, apimethod, RequestContainer
from ripozo.resources.constructor import ResourceMetaClass
from ripozo.resources.restmixins import Create, Retrieve, Update, \
    Delete, RetrieveRetrieveList, AllOptionsResource

import mock
import unittest2


class TestMixins(unittest2.TestCase):

    def setUp(self):
        ResourceMetaClass.registered_names_map = {}
        ResourceMetaClass.registered_resource_classes = {}

    def get_fake_manager(self):
        manager = mock.MagicMock()
        manager.rest_route = False
        manager.__rest_route__ = False
        return manager

    def test_create(self):
        manager2 = mock.MagicMock()

        class T1(Create):
            manager = manager2

        request = mock.MagicMock()
        response = T1.create(request)
        # self.assertEqual(request.translate.call_count, 1)
        self.assertEqual(manager2.create.call_count, 1)
        self.assertIsInstance(response, T1)

    def test_create_has_apimethod(self):
        """
        Tests that the endpoint_dictionary gets the
        result
        """
        class T1(Create):
            manager = self.get_fake_manager()
        endpoints = T1.endpoint_dictionary()
        self.assertEqual(len(endpoints), 1)

    def test_retrieve_list(self):
        manager2 = mock.MagicMock()
        manager2.retrieve_list = mock.MagicMock(return_value=(mock.MagicMock(), mock.MagicMock()))

        class T1(RetrieveRetrieveList):
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
        # self.assertEqual(request.translate.call_count, 1)
        self.assertEqual(manager2.retrieve.call_count, 1)
        self.assertIsInstance(response, T1)

    def test_update(self):
        manager2 = mock.MagicMock()

        class T1(Update):
            manager = manager2

        request = mock.MagicMock()
        response = T1.update(request)
        # self.assertEqual(request.translate.call_count, 1)
        self.assertEqual(manager2.update.call_count, 1)
        self.assertIsInstance(response, T1)

    def test_delete(self):
        manager2 = mock.MagicMock()

        class T1(Delete):
            manager = manager2

        request = mock.MagicMock()
        response = T1.delete(request)
        # self.assertEqual(request.translate.call_count, 1)
        self.assertEqual(manager2.delete.call_count, 1)
        self.assertIsInstance(response, T1)

    def test_all_options_links_no_pks(self):
        """
        Tests getting the links for a class with
        only no_pks apimethods
        """
        class Fake(ResourceBase):
            @apimethod(no_pks=True)
            def fake(cls, request):
                return cls()

        class MyResource(AllOptionsResource):
            linked_resource_classes = (Fake,)

        links = MyResource.links
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertEqual(link.relation, Fake)
        self.assertEqual(link.name, 'fake_list')
        self.assertTrue(link.no_pks)

    def test_all_options_links_with_pks(self):
        """
        Tests getting the links for a class with
        only no_pks apimethods
        """
        class Fake(ResourceBase):
            @apimethod()
            def fake(cls, request):
                return cls()

        class MyResource(AllOptionsResource):
            linked_resource_classes = (Fake,)

        links = MyResource.links
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertEqual(link.relation, Fake)
        self.assertEqual(link.name, 'fake')
        self.assertFalse(link.no_pks)

    def test_all_options(self):
        """
        Tests calling the all_options route
        and constructing all of the links.
        """
        class Fake(ResourceBase):
            pks = ('id',)
            @apimethod()
            def fake(cls, request):
                return cls()

            @apimethod(no_pks=True)
            def fake2(cls, request):
                return cls()

        class MyResource(AllOptionsResource):
            linked_resource_classes = (Fake,)

        options = MyResource.all_options(RequestContainer())
        self.assertEqual(len(options.linked_resources), 2)
        found_fake = False
        found_fake_list = False
        for l in options.linked_resources:
            rel = l.resource
            if l.name == 'fake':
                self.assertEqual(rel.url, '/fake/<id>')
                found_fake = True
            if l.name == 'fake_list':
                self.assertEqual(rel.url, '/fake')
                found_fake_list = True
        self.assertTrue(found_fake)
        self.assertTrue(found_fake_list)
