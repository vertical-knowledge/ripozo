from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.resources.relationships.list_relationship import ListRelationship
from ripozo.resources.resource_base import ResourceBase

import unittest2


class TestListRelationship(unittest2.TestCase):
    """
    Tests the ListRelationship class
    """

    def test_init(self):
        """
        Tests the initialization of the ListRelationship
        """
        list_name = 'mylist'
        lr = ListRelationship(list_name, relation='MyResource', embedded=True)
        self.assertEqual(list_name, lr.name)
        self.assertTrue(lr.embedded)
        self.assertEqual(lr._relation, 'MyResource')

    def test_construct_resource(self):
        class RelatedResource(ResourceBase):
            _pks = ['pk']

        list_name = 'mylist'
        lr = ListRelationship(list_name, relation='RelatedResource')
        props = {list_name: []}
        for i in range(10):
            props[list_name].append(dict(pk=i))
        res_list = lr.construct_resource(props)
        self.assertIsInstance(res_list, list)
        for x in res_list:
            # TODO actually check this
            pass
        self.assertEqual(len(res_list), 10)

    def test_empty_list(self,):
        class RelatedResource2(ResourceBase):
            pass
        list_name = 'mylist'
        lr = ListRelationship(list_name, relation='RelatedResource')
        res_list = lr.construct_resource(dict(some='thing', another='thing'))
        self.assertIsInstance(res_list, list)
        self.assertEqual(len(res_list), 0)

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
