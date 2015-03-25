from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.request import RequestContainer

from ripozo_tests.python2base import TestBase

import unittest


class TestRequestContainer(TestBase, unittest.TestCase):
    """
    Tests for the RequestContainer
    """

    def test_url_params(self):
        self.dict_helper('url_params')

    def test_query_args(self):
        self.dict_helper('query_args')

    def test_body_args(self):
        self.dict_helper('body_args')

    def test_headers(self):
        self.dict_helper('headers')

    def test_content_type(self):
        content_type = 'for real;'
        headers = {'Content-Type': content_type}
        r = RequestContainer(headers=headers)
        self.assertEqual(content_type, r.content_type)
        r = RequestContainer()
        self.assertIsNone(r.content_type)

        # set the content type
        r.content_type = 'blah'
        self.assertEqual(r.content_type, 'blah')


    def dict_helper(self, name):
        d = dict(some='object')
        r = RequestContainer(**{name: d})
        self.assertDictEqual(d, getattr(r, name))
        self.assertNotEqual(id(d), id(getattr(r, name)))

        # Test setting the dict
        d2 = dict(another='object')
        setattr(r, name, d2)
        self.assertNotEqual(d, getattr(r, name))
        self.assertDictEqual(d2, getattr(r, name))
        self.assertNotEqual(id(d2), id(getattr(r, name)))

        # Test empty dict
        r = RequestContainer()
        self.assertIsInstance(getattr(r, name), dict)
