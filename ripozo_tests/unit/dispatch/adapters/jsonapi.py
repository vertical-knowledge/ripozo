from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import unittest2

from ripozo import ResourceBase
from ripozo.adapters.jsonapi import JSONAPIAdapter


class TestJSONAPIAdapter(unittest2.TestCase):
    def test_construct_pks_no_pks(self):
        """When there are no ids"""
        class MyResource(ResourceBase):
            pks = tuple()

        response = JSONAPIAdapter._construct_id(MyResource())
        self.assertEqual(response, '')

    def test_construct_pks_one_pk(self):
        """Constructing a single id"""
        class MyResource(ResourceBase):
            pks = 'id',

        response = JSONAPIAdapter._construct_id(MyResource(properties=dict(id=1)))
        self.assertEqual(response, '1')

    def test_construct_pks_multiple_pks(self):
        """Constructing a single id from multiple"""
        class MyResource(ResourceBase):
            pks = 'id', 'pk'

        response = JSONAPIAdapter._construct_id(MyResource(properties=dict(id=1, pk=2)))
        self.assertEqual(response, '1/2')

