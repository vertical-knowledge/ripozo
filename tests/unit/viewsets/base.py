from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import six

from rest.decorators import apimethod
from rest.exceptions import BaseRestEndpointAlreadyExists
from rest.viewsets.constructor import ResourceMetaClass
from rest.viewsets.resource_base import ResourceBase
from tests.unit.helpers.inmemory_manager import InMemoryManager
from tests.python2base import TestBase


logger = logging.getLogger(__name__)


class MM1(InMemoryManager):
    model = 'Something'
    _model_name = 'modelname'

name_space = '/mynamspace/'


class TestResource(ResourceBase):
    __abstract__ = True
    _manager = MM1
    _resource_name = 'myresource'
    _namespace = name_space


class TestResourceBase(TestBase):
    def setUp(self):
        ResourceMetaClass.registered_resource_classes.clear()

    def test_abstract_not_implemented(self):
        """
        asserts that a class that inherits from
        resource base with __abstract__ == True
        is not registered on the ResourceMetaClass
        """
        class TestResourceClass(ResourceBase):
            __abstract__ = True
        self.assertEqual(len(ResourceMetaClass.registered_resource_classes), 0)

    def test_resource_name(self):
        """Tests whether the resource_name is properly constructed"""
        resourcename = 'myresource'

        class T1(TestResource):
            __resource_name__ = resourcename
        self.assertEqual(resourcename, T1.resource_name)

    def test_resource_name2(self):
        """
        Tests whether the resource_name is properly retrieved from
        manager if the resource_name is not specified.
        """
        class T2(TestResource):
            _resource_name = None

            __manager__ = MM1
        self.assertEqual(T2.resource_name, T2.__manager__()._model_name)

    def test_model_name(self):
        """Tests whether the model name is retrieved from manager"""
        class T1(TestResource):
            __manager__ = MM1
        self.assertEqual(T1.model_name, MM1().model_name)

    def test_manager_property(self):
        """Tests whether the manager instance is properly instantiated"""
        class T1(TestResource):
            __manager__ = MM1
        self.assertIsInstance(T1.manager, MM1)

    def test_base_url(self):
        """Tests whether the base_url is properly constructed"""
        class T1(TestResource):
            pks = ['something', 'another_thing']
        self.assertIsInstance(T1.base_url, six.text_type)
        self.assertIn(name_space, T1.base_url)
        self.assertIn(T1.resource_name, T1.base_url)
        for pk in T1.pks:
            self.assertIn(pk, T1.base_url)

    def test_class_registered(self):
        """Tests whether an implement Resource is registered on the meta class"""
        class T1(TestResource):
            pass
        self.assertIn(T1, six.iterkeys(ResourceMetaClass.registered_resource_classes))

    def test_register_endpoint(self):
        """Tests whether the endpoint is registered on the class"""
        class T1(TestResource):
            @apimethod(methods=['GET'])
            def my_api_method1(self):
                pass
        # for python 3.3  Otherwise it never gets registered for some reason
        print(T1.__name__)

        self.assertIn('my_api_method1', T1.endpoint_dictionary)

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

    def test_url_property(self):
        """Tests whether the url for an individual resource is properly created"""
        class T1(TestResource):
            namespace = '/api'
            pks = ['pk']
            _resource_name = 'my_resource'

        x = T1(properties={'pk': 1})
        self.assertEqual(x.url, '/api/my_resource/1')
