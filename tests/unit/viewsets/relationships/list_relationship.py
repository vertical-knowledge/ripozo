from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.relationships.list_relationship import ListRelationship

from ripozo_tests.python2base import TestBase

import mock
import types
import unittest


class TestListRelationship(TestBase, unittest.TestCase):
    """
    Tests the ListRelationship class
    """

    def test_init(self):
        """
        Tests the initialization of the ListRelationship
        """
        list_name = 'mylist'
        lr = ListRelationship(list_name, relation='MyResource', embedded=True)
        self.assertEqual(list_name, lr.list_name)
        self.assertTrue(lr.embedded)
        self.assertEqual(lr._relation, 'MyResource')

    @mock.patch.object(ListRelationship, 'relation')
    def test_construct_resource(self, mck):
        list_name = 'mylist'
        lr = ListRelationship(list_name)
        props = {list_name: range(10)}
        generator = lr.construct_resource(props)
        self.assertIsInstance(generator, types.GeneratorType)
        for x in generator:
            pass

        self.assertEquals(mck.call_count, 10)

    @mock.patch.object(ListRelationship, 'relation')
    def test_empty_list(self, mck):
        list_name = 'mylist'
        lr = ListRelationship(list_name)
        generator = lr.construct_resource(dict(some='thing', another='thing'))
        self.assertIsInstance(generator, types.GeneratorType)

        # There are no acceptable generators
        for x in generator:
            assert False

        self.assertEqual(mck.call_count, 0)

    def test_remove_child_properties(self):
        """
        Test remove child properties
        """
        list_name = 'listname'
        properties = {list_name: 'Something', 'another': 'thing'}
        lr = ListRelationship(list_name)
        post_props = lr.remove_child_resource_properties(properties)
        self.assertNotEqual(properties, post_props)
        self.assertEqual({'another': 'thing'}, post_props)

        # Just make sure that it still works when the properties aren't there
        part2 = lr.remove_child_resource_properties(post_props)
        self.assertEqual(part2, post_props)
        self.assertNotEqual(id(part2), id(post_props))
