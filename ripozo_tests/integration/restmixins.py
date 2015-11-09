from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo import restmixins, RequestContainer, ResourceBase

from ripozo_tests.helpers.inmemory_manager import InMemoryManager

import unittest2
import uuid


class TestBase(unittest2.TestCase):
    def setUp(self):
        class MyManager(InMemoryManager):
            fields = ('id', 'first', 'second',)
            paginate_by = 5

        class MyClass(self.resource_base):
            manager = MyManager()
            pks = ('id',)

        self.resource_class = MyClass
        self.manager = MyClass.manager

    def create_resources(self, count=3):
        all_models = []
        for i in range(count):
            id_ = uuid.uuid4()
            model = dict(id=id_, first=1, second=2)
            self.manager.objects[id_] = model
            all_models.append(model)
        return all_models

    def assertListEquivalent(self, l1, l2):
        """Getting some weird issue in pypy where
        a list is getting flipped.  It is not critical
        to be ordered so this is a temporary fix"""
        # TODO figure out what is going on in pypy
        self.assertEqual(len(l1), len(l2))
        for item in l1:
            self.assertIn(item, l2)


class TestCreate(TestBase):
    resource_base = restmixins.Create

    def test_create(self):
        body = dict(first=1, second=2)
        req = RequestContainer(body_args=body)
        resource = self.resource_class.create(req)
        self.assertIsInstance(resource, restmixins.Create)
        resource_id = resource.properties.get('id')
        body.update(dict(id=resource_id))
        self.assertDictEqual(body, resource.properties)
        actual_obj = self.manager.objects[resource_id]
        self.assertDictEqual(actual_obj, resource.properties)

    def test_create_link(self):
        body = dict(first=1, second=2)
        req = RequestContainer(body_args=body)
        resource = self.resource_class.create(req)
        self.assertEqual(len(resource.linked_resources), 1)
        created = resource.linked_resources[0]
        self.assertEqual(created.name, 'created')
        self.assertIsInstance(created.resource, self.resource_class)
        self.assertEqual(created.resource.properties, resource.properties)

    def test_create_manager_fields(self):
        """
        Tests that the manager fields
        are available
        """
        fields = self.resource_class.create.fields(self.manager)
        for field in fields:
            self.assertIn(field.name, self.manager.fields)
        self.assertEqual(len(fields), len(self.manager.fields))

    def test_create_translate_fields(self):
        """Ensures that only the create_fields
        are available"""
        class CreateManager(InMemoryManager):
            fields = 'id', 'first', 'second',
            create_fields = 'first', 'second',

        class CreateResource(self.resource_base):
            manager = CreateManager()
            pks = 'id',

        names = [f.name for f in CreateResource.create.fields(CreateResource.manager)]
        self.assertListEquivalent(('second', 'first',), tuple(names))



class TestRetrieve(TestBase):
    resource_base = restmixins.Retrieve

    def test_retrieve(self):
        id_ = uuid.uuid4()
        model = dict(id=id_, first=1, second=2)
        self.manager.objects[model['id']] = model
        req = RequestContainer(url_params=dict(id=id_))
        resource = self.resource_class.retrieve(req)
        self.assertDictEqual(resource.properties, model)


class TestRetrieveList(TestBase):
    resource_base = restmixins.RetrieveList

    def test_retrieve_list(self):
        all_models = self.create_resources(count=3)
        req = RequestContainer()
        resource = self.resource_class.retrieve_list(req)

        for res in resource.properties[resource.resource_name]:
            self.assertIn(res, self.manager.objects.values())

    def test_url(self):
        req = RequestContainer()
        resource = self.resource_class.retrieve_list(req)
        self.assertEqual(resource.url, '/my_class')

    def test_filters(self):
        all_models = self.create_resources(count=10)
        req = RequestContainer(query_args=dict(first=1))
        resource = self.resource_class.retrieve_list(req)
        self.assertEqual(resource.get_query_arg_dict()['first'], 1)

    def test_get_base_links(self):
        class R(ResourceBase):
            pass
        resp = restmixins.RetrieveList.get_base_links(R)
        self.assertTupleEqual(resp[0].query_args, tuple())

    def test_paginate(self):
        all_models = self.create_resources(count=10)
        req = RequestContainer()
        resource = self.resource_class.retrieve_list(req)
        next_link = None
        for r in resource.linked_resources:
            if r.name == 'next':
                next_link = r
                break
        else:
            assert False
        self.assertEqual(next_link.name, 'next')
        next_resource = next_link.resource
        self.assertIsInstance(next_resource, self.resource_class)

        self.assertIn(self.manager.pagination_count_query_arg, next_resource.get_query_arg_dict())
        self.assertIn(self.manager.pagination_pk_query_arg, next_resource.get_query_arg_dict())

        req = RequestContainer(query_args=next_resource.get_query_arg_dict())
        resource = self.resource_class.retrieve_list(req)
        prev_link = None
        for r in resource.linked_resources:
            if r.name == 'previous':
                prev_link = r
                break
        else:
            assert False
        self.assertEqual(prev_link.name, 'previous')
        prev_resource = prev_link.resource
        self.assertIsInstance(prev_resource, self.resource_class)

        self.assertIn(self.manager.pagination_count_query_arg, prev_resource.get_query_arg_dict())
        self.assertIn(self.manager.pagination_pk_query_arg, prev_resource.get_query_arg_dict())

    def test_retrieve_list_manager_fields(self):
        """
        Tests that the manager fields
        are available
        """
        fields = self.resource_class.retrieve_list.fields(self.resource_class.manager)
        for field in fields:
            self.assertIn(field.name, self.manager.fields)
        self.assertEqual(len(fields), len(self.manager.fields))

    def test_list_translate_fields(self):
        """Ensures that only the create_fields
        are available"""
        class ListManager(InMemoryManager):
            fields = 'id', 'first', 'second',
            list_fields = 'first', 'second',

        class ListResource(self.resource_base):
            manager = ListManager()
            pks = 'id',

        names = [f.name for f in ListResource.retrieve_list.fields(ListResource.manager)]
        self.assertListEquivalent(('second', 'first',), tuple(names))


class TestRetrieveRetrieveList(TestRetrieve, TestRetrieveList):
    resource_base = restmixins.RetrieveRetrieveList

    def test_retrieve_list(self):
        all_models = self.create_resources(count=3)
        req = RequestContainer()
        resource = self.resource_class.retrieve_list(req)

        sub_resources = None
        for r in resource.related_resources:
            if r.name == self.resource_class.resource_name:
                sub_resources = r
                break
        else:
            assert False
        self.assertEqual(sub_resources.name, self.resource_class.resource_name)
        sub_resources = sub_resources.resource

        for res in sub_resources:
            self.assertIn(res.properties, self.manager.objects.values())
            self.assertIsInstance(res, self.resource_class)


class TestUpdate(TestBase):
    resource_base = restmixins.Update

    def test_update(self):
        id_ = uuid.uuid4()
        model = dict(id=id_, first=1, second=2)
        self.manager.objects[model['id']] = model
        req = RequestContainer(url_params=dict(id=id_), body_args=dict(first=2))
        resource = self.resource_class.update(req)
        for k, v in resource.properties.items():
            if k is not 'first':
                self.assertEqual(v, model[k])
            else:
                self.assertEqual(v, 2)

    def test_update_manager_fields(self):
        """
        Tests that the manager fields
        are available
        """
        fields = self.resource_class.update.fields(self.resource_class.manager)
        for field in fields:
            self.assertIn(field.name, self.manager.fields)
        self.assertEqual(len(fields), len(self.manager.fields))

    def test_update_translate_fields(self):
        """Ensures that only the update_fields
        are available"""
        class UpdateManager(InMemoryManager):
            fields = 'id', 'first', 'second',
            update_fields = 'first', 'second',

        class UpdateResource(self.resource_base):
            manager = UpdateManager()
            pks = 'id',

        names = [f.name for f in UpdateResource.update.fields(UpdateResource.manager)]
        self.assertListEquivalent(('second', 'first',), tuple(names))


class TestDelete(TestBase):
    resource_base = restmixins.Delete

    def test_delete(self):
        id_ = uuid.uuid4()
        model = dict(id=id_, first=1, second=2)
        self.manager.objects[id_] = model
        req = RequestContainer(url_params=dict(id=id_), body_args=dict(first=2))
        resource = self.resource_class.delete(req)
        self.assertDictEqual(resource.properties, {})
        self.assertNotIn(id_, self.manager.objects)

    def test_delete_manager_fields(self):
        """
        Tests that the manager fields
        are available
        """
        fields = self.resource_class.delete.fields(self.resource_class.manager)
        for field in fields:
            self.assertIn(field.name, self.manager.fields)
        self.assertEqual(len(fields), len(self.manager.fields))


class TestRetrieveUpdate(TestRetrieve, TestUpdate):
    resource_base = restmixins.RetrieveUpdate


class TestRetrieveUpdateDelete(TestRetrieve, TestUpdate, TestDelete):
    resource_base = restmixins.RetrieveUpdateDelete


class TestCreateRetrieve(TestCreate, TestRetrieve):
    resource_base = restmixins.CreateRetrieve


class TestCreateRetrieveUpdate(TestCreate, TestRetrieve, TestUpdate):
    resource_base = restmixins.CreateRetrieveUpdate


class TestCRUD(TestCreate, TestRetrieve, TestUpdate, TestDelete):
    resource_base = restmixins.CRUD


class TestCRUDL(TestCreate, TestRetrieveRetrieveList, TestUpdate, TestDelete):
    resource_base = restmixins.CRUDL
