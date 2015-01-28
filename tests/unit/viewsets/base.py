from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest.decorators import apimethod
from rest.exceptions import BaseRestEndpointAlreadyExists
from rest.viewsets.base2 import ResourceMetaClass
from rest.viewsets.resource_base import ResourceBase
from tests.unit.helpers.inmemory_manager import InMemoryManager

import six
import unittest


class MM1(InMemoryManager):
    model = 'Something'
    _model_name = 'modelname'

name_space = '/mynamspace/'


class TestResource(ResourceBase):
    __abstract__ = True
    resource_name = 'myresource'
    manager = MM1
    namespace = name_space


class TestResourceBase(unittest.TestCase):
    # TODO documentation

    def tearDown(self):
        ResourceMetaClass.registered_resource_classes.clear()

    def test_abstract_not_implemented(self):
        """
        asserts that a class that inherits from
        resource base with __abstract__ == True
        is not registered on the ResourceMetaClass
        """
        class TestResourceClass(ResourceBase):
            __abstract__ = True
        self.assertEquals(len(ResourceMetaClass.registered_resource_classes), 0)

    def test_resource_name(self):
        """Tests whether the resource_name is properly constructed"""
        resourcename = 'myresource'
        class T1(TestResource):
            resource_name = resourcename
        self.assertEqual(resourcename, T1._resource_name)

    def test_resource_name2(self):
        """
        Tests whether the resource_name is properly retrieved from
        manager if the resource_name is not specified.
        """
        class T2(TestResource):
            resource_name = None
            manager = MM1
        self.assertEqual(T2._resource_name, T2.manager()._model_name)

    def test_model_name(self):
        """Tests whether the model name is retrieved from manager"""
        class T1(TestResource):
            manager = MM1
        self.assertEqual(T1.model_name, MM1().model_name)

    def test_manager_property(self):
        """Tests whether the manager instance is properly instantiated"""
        class T1(TestResource):
            manager = MM1
        self.assertIsInstance(T1._manager, MM1)

    def test_base_url(self):
        """Tests whether the base_url is properly constructed"""
        class T1(TestResource):
            pks = ['something', 'another_thing']
        self.assertIsInstance(T1.base_url, six.text_type)
        self.assertIn(name_space, T1.base_url)
        self.assertIn(T1._resource_name, T1.base_url)
        for pk in T1.pks:
            self.assertIn(pk, T1.base_url)

    def test_class_registered(self):
        """Tests whether an implement Resource is registered on the meta class"""
        class T1(TestResource):
            pass
        self.assertIn(T1, ResourceMetaClass.registered_resource_classes.keys())

    def test_register_endpoint(self):
        """Tests whether the endpoint is registered on the class"""
        class T1(TestResource):
            @apimethod(methods=['GET'])
            def my_api_method1(self):
                pass

        self.assertIn('my_api_method1', T1._endpoint_dictionary)

    def test_base_url_duplication_exception(self):
        """Tests whether an excption is raised if the base_url
        already exists"""
        class T1(TestResource):
            pass

        try:
            class T2(TestResource):
                pass
            assert False
        except BaseRestEndpointAlreadyExists:
            pass

    def test_init(self):
        """Just tests whether the __init__ method initializes without exception"""
        class T1(TestResource):
            pass
        # TODO add more once you determine exactly what the __init__ should do
        x = T1()
