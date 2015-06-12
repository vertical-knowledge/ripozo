from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import types

import mock
import six
import unittest2

from ripozo.decorators import apimethod
from ripozo.resources.constructor import ResourceMetaClass
from ripozo.resources.relationships import Relationship, ListRelationship
from ripozo.resources.resource_base import ResourceBase, _get_apimethods
from ripozo_tests.helpers.inmemory_manager import InMemoryManager

logger = logging.getLogger(__name__)


class MM1(InMemoryManager):
    model = 'Something'
    _model_name = 'modelname'

name_space = '/mynamspace/'


class TestResource(ResourceBase):
    __abstract__ = True
    manager = MM1()
    resource_name = 'myresource'
    namespace = name_space


class TestResourceBase(unittest2.TestCase):
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
            resource_name = resourcename
        self.assertEqual(resourcename, T1.resource_name)

    def test_manager_property(self):
        """Tests whether the manager instance is properly instantiated"""
        class T1(TestResource):
            manager = MM1()
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

    def test_minimal_base_url(self):
        """Tests the url when no resource name or namespace is specified"""
        class SomeResource(ResourceBase):
            pass

        self.assertEqual('/some_resource', SomeResource.base_url)

        class AnotherResource(ResourceBase):
            resource_name = 'another_resource'

        self.assertEqual('/another_resource', AnotherResource.base_url)

        class FinalResource(ResourceBase):
            namespace = '/api'

        self.assertEqual('/api/final_resource', FinalResource.base_url)

    def test_messed_up_slashes_on_base_url(self):
        """Tests whether the ResourceBase always appropriately replaces
        forward slashes on urls"""
        class DoubleSlash(ResourceBase):
            namespace = '/'
            resource_name = '/'

        self.assertEqual('/', DoubleSlash.base_url)
        ResourceMetaClass.registered_resource_classes.clear()

        class DoublSlash2(ResourceBase):
            namespace = '//'
            resource_name = '/double_slash'

        self.assertEqual('/double_slash', DoublSlash2.base_url)
        ResourceMetaClass.registered_resource_classes.clear()

        class DoubleMiddleSlash(ResourceBase):
            namespace = 'api/'
            resource_name = '//another_resource/'

        self.assertEqual('/api/another_resource/', DoubleMiddleSlash.base_url)

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

        self.assertIn('my_api_method1', T1.endpoint_dictionary())

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
            resource_name = 'my_resource'

        x = T1(properties={'pk': 1})
        self.assertEqual(x.url, '/api/my_resource/1')

    def test_multiple_resources_endpoint_dictionaries(self):
        """
        Ran into a bug where the _endpoint_dictionary was getting
        overridden and therefore all resources returned the same
        endpoints
        """

        class T1(ResourceBase):
            @apimethod(methods=['GET'])
            def hello(cls, *args, **kwargs):
                return cls(properties=dict(hello='world'))

        endpoint = T1.endpoint_dictionary()['hello'][0]
        self.assertEqual(endpoint['route'], '/t1/')
        self.assertListEqual(endpoint['methods'], ['GET'])

        # The routes in this should be different
        class T2(T1):
            pass

        # Ensure the T1 endpoint dictionary is the same as before
        endpoint = T1.endpoint_dictionary()['hello'][0]
        self.assertEqual(endpoint['route'], '/t1/')
        self.assertListEqual(endpoint['methods'], ['GET'])

        # Make sure the T2 endpoint dictionary has a different route
        endpoint = T2.endpoint_dictionary()['hello'][0]
        self.assertEqual(endpoint['route'], '/t2/')
        self.assertListEqual(endpoint['methods'], ['GET'])

    def test_multiple_subclasses(self):
        """
        tests whether multiple classes can inherit from the same
        abstract class
        """
        props = dict(hello='world')
        class T1(ResourceBase):
            @apimethod(methods=['GET'])
            def hello(cls, *args, **kwargs):
                return cls(properties=dict(hello='world'))

        endpoint = T1.endpoint_dictionary()['hello'][0]
        self.assertEqual(endpoint['route'], '/t1/')
        self.assertListEqual(endpoint['methods'], ['GET'])
        self.assertDictEqual(props, T1.hello(mock.MagicMock()).properties)

        class T2(T1):
            pass

        class T3(T1):
            pass

        class T4(T2):
            pass

        endpoint = T1.endpoint_dictionary()['hello'][0]
        self.assertEqual(endpoint['route'], '/t1/')
        self.assertListEqual(endpoint['methods'], ['GET'])
        self.assertDictEqual(props, T1.hello(mock.MagicMock()).properties)

        endpoint = T2.endpoint_dictionary()['hello'][0]
        self.assertEqual(endpoint['route'], '/t2/')
        self.assertListEqual(endpoint['methods'], ['GET'])
        self.assertDictEqual(props, T1.hello(mock.MagicMock()).properties)

        endpoint = T3.endpoint_dictionary()['hello'][0]
        self.assertEqual(endpoint['route'], '/t3/')
        self.assertListEqual(endpoint['methods'], ['GET'])
        self.assertDictEqual(props, T1.hello(mock.MagicMock()).properties)

        endpoint = T4.endpoint_dictionary()['hello'][0]
        self.assertEqual(endpoint['route'], '/t4/')
        self.assertListEqual(endpoint['methods'], ['GET'])
        self.assertDictEqual(props, T1.hello(mock.MagicMock()).properties)

    def test_has_error(self):
        """
        Test the has_error property
        """
        class T1(ResourceBase):
            pass

        r = T1(errors=[])
        self.assertFalse(r.has_error)
        r = T1(errors=[1])
        self.assertTrue(r.has_error)
        r = T1(status_code=400)
        self.assertTrue(r.has_error)

    def test_links_property(self):
        """
        Tests that the links property appropriately creates link relationships.
        """
        class T1(ResourceBase):
            _resource_name = 'resource'
            _pks = ['id']

        meta = dict(links=dict(link=dict(id='a')))
        resource = T1(meta=meta)

    def test_get_apimethods(self):
        """
        Tests that the function _get_apimethods
        appropriately gets apimethods and that they
        are class methods not _apiclassmethod instances.
        """
        class MyResource(ResourceBase):
            @apimethod(methods=['GET'])
            @apimethod(methods=['POST'])
            def fake1(cls):
                pass

            @apimethod(route='/hey', methods=['GET'])
            def fake2(self):
                pass

        names = []
        for name, clsmethod in _get_apimethods(MyResource):
            names.append(name)
            self.assertIsInstance(clsmethod, types.FunctionType)
        self.assertIn('fake1', names)
        self.assertIn('fake2', names)
        self.assertEqual(len(names), 2)

    def test_run_get_apimethods(self):
        """
        Tests whether the methods returned by _get_apimethods
        can be run raw.
        """
        class MyResource(ResourceBase):
            @apimethod(methods=['GET'])
            def fake(cls, request, *args, **kwargs):
                return cls, request

        request = object()
        for name, clsmethod in _get_apimethods(MyResource):
            klass, response = clsmethod(request)
            self.assertEqual(MyResource, klass)
            self.assertEqual(id(request), id(response))

    def test_generate_links(self):
        """
        Tests the private _generate_links staticmethod
        """
        class Related(ResourceBase):
            _pks = ['id']

        rel_list = [Relationship(name='first', relation='Related')]
        props = dict(first=dict(id=1, other_value='something'))
        resource_list = ResourceBase._generate_links(rel_list, props.copy())
        resource, name, embedded = resource_list[0]
        self.assertFalse(embedded)
        self.assertEqual(props['first'], resource.properties)

    def test_generate_links_list(self):
        """
        Tests the private _generate_links staticmethod
        with a ListRelationship
        """
        class Related(ResourceBase):
            _pks = ['id']

        rel_list = [ListRelationship('relations', relation='Related')]
        props = dict(relations=[dict(id=1), dict(id=2)])
        resource_list = ResourceBase._generate_links(rel_list, props.copy())
        resource, name, embedded = resource_list[0]
        self.assertIsInstance(resource, list)
        self.assertEqual(len(resource), 2)
        for res in resource:
            self.assertIsInstance(res, Related)

    def test_construct_self_referential(self):
        """
        Tests trying to use a self-referential relationship
        when constructing a resource
        """
        class Resource(ResourceBase):
            _pks = ['id']
            _relationships = [
                Relationship('child', relation='Resource', embedded=True),
                Relationship('parent', relation='Resource')
            ]

        res = Resource(properties=dict(id=1))
        self.assertEqual(len(res.related_resources), 0)

        res = Resource(properties=dict(id=1, child=dict(id=2)))
        self.assertEqual(len(res.related_resources), 1)
        relation = res.related_resources[0][0]
        self.assertIsInstance(relation, Resource)

        res = Resource(properties=dict(id=1, child=dict(id=2, parent=dict(id=1))))
        self.assertEqual(len(res.related_resources), 1)
        relation = res.related_resources[0][0]
        self.assertIsInstance(relation, Resource)

        self.assertEqual(len(relation.related_resources), 1)
        parent = res.related_resources[0][0]
        self.assertIsInstance(parent, Resource)

    def test_get_apimethods_multiwrapped(self):
        class MyResource(ResourceBase):
            @apimethod(methods=['GET'])
            @apimethod(methods=['POST'])
            def fake(cls, *args, **kwargs):
                args = (cls,) + args
                return args, kwargs

        count = 0
        for name, method in _get_apimethods(MyResource):
            count += 1
            self.assertEqual(name, 'fake')
        self.assertEqual(count, 1)

    def test_self_referential_relationships(self):
        class Resource1(ResourceBase):
            _pks = ['id']
            _relationships = [Relationship('resource2', relation='Resource2')]

        class Resource2(ResourceBase):
            _pks = ['id']
            _relationships = [Relationship('resource1', relation='Resource1')]

        res = Resource1(dict(id=1, resource2=dict(id=2)))
        self.assertEqual(len(res.related_resources), 1)
        related = res.related_resources[0][0]
        self.assertEqual(len(related.related_resources), 0)

    def test_has_all_pks_property(self):
        """
        Tests the has_all_pks instance property
        """
        class Fake1(ResourceBase):
            pass

        res = Fake1()
        self.assertTrue(res.has_all_pks)

        class Fake2(ResourceBase):
            pks = ('id', 'pk',)

        res = Fake2(properties=dict(id=1, pk=2))
        self.assertTrue(res.has_all_pks)
        res = Fake2(properties=dict(id=1))
        self.assertFalse(res.has_all_pks)

    def test_url_prop_with_query_args(self):
        """
        Tests that query args get added to
        the url property appropriately
        """
        class Fake(ResourceBase):
            _resource_name = 'fake'

        res = Fake(properties=dict(param=2, other=4), query_args=['param', 'other'])
        self.assertIn(res.url, ['/fake?other=4&param=2', '/fake?param=2&other=4'])

    def test_base_url_sans_pks(self):
        """
        Tests the class property for the
        base_url_sans_pks property on the
        ResourceBase class
        """
        class Fake(ResourceBase):
            resource_name = 'api'

        self.assertEqual(Fake.base_url_sans_pks, '/api')

        class Fake2(ResourceBase):
            namespace = 'api'

        self.assertEqual(Fake2.base_url_sans_pks, '/api/fake2')

        class Fake3(ResourceBase):
            resource_name = 'fake'
            namespace = 'api'

        self.assertEqual(Fake3.base_url_sans_pks, '/api/fake')

        class Fake4(ResourceBase):
            namespace = '/api'

        self.assertEqual(Fake4.base_url_sans_pks, '/api/fake4')

    def test_inherit_resource_name(self):
        """
        Tests that the resource_name property gets
        reset when inheritied.
        """
        class Resource1(ResourceBase):
            pass
        self.assertEqual(Resource1.resource_name, 'resource1')

        class Resource2(Resource1):
            pass
        self.assertEqual(Resource2.resource_name, 'resource2')
        self.assertEqual(Resource1.resource_name, 'resource1')
        self.assertEqual(ResourceBase.resource_name, 'resource_base')
