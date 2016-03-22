from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest2

from ripozo.resources.constants.input_categories import QUERY_ARGS, BODY_ARGS, URL_PARAMS
from ripozo.resources.request import RequestContainer


class TestRequestContainer(unittest2.TestCase):
    """
    Tests for the RequestContainer
    """

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

    def test_get(self):
        """
        Tests that the get method appropriately retrieves
        paramaters.
        """
        r = RequestContainer(url_params=dict(key=1, key2=2))
        self.assertEqual(r.get('key'), 1)
        self.assertEqual(r.get('key2'), 2)

        r = RequestContainer(query_args=dict(key=1, key2=2))
        self.assertEqual(r.get('key'), 1)
        self.assertEqual(r.get('key2'), 2)

        r = RequestContainer(body_args=dict(key=1, key2=2))
        self.assertEqual(r.get('key'), 1)
        self.assertEqual(r.get('key2'), 2)

        r = RequestContainer(url_params=dict(key=1), query_args=dict(key=2), body_args=dict(key=3))
        self.assertEqual(r.get('key'), 1)

    def test_get_not_found(self):
        """
        Tests the get with a default value
        """
        r = RequestContainer()
        self.assertEqual(r.get('fake', 'hey'), 'hey')
        self.assertEqual(r.get('fak'), None)

    def test_set_key_error(self):
        """
        Asserts that set raises a key error
        when the value cannot be found.
        """
        req = RequestContainer(query_args=dict(x=1))
        self.assertRaises(KeyError, req.set, 'blah', 'blah')

    def test_set(self):
        """
        Tests the basic set on the request
        without location specified
        """
        original_dict = dict(x=1)
        req = RequestContainer(query_args=original_dict)
        req.set('x', 2)
        self.assertDictEqual(dict(x=2), req.query_args)

        req = RequestContainer(url_params=original_dict)
        req.set('x', 2)
        self.assertDictEqual(dict(x=2), req.url_params)

        req = RequestContainer(body_args=original_dict)
        req.set('x', 2)
        self.assertDictEqual(dict(x=2), req.body_args)

    def test_set_location_specified(self):
        """
        Tests the set on the request container
        with the location specified.
        """
        original_dict = dict(x=1)
        req = RequestContainer(query_args=original_dict)
        req.set('x', 2, QUERY_ARGS)
        self.assertDictEqual(dict(x=2), req.query_args)

        req = RequestContainer(url_params=original_dict)
        req.set('x', 2, URL_PARAMS)
        self.assertDictEqual(dict(x=2), req.url_params)

        req = RequestContainer(body_args=original_dict)
        req.set('x', 2, BODY_ARGS)
        self.assertDictEqual(dict(x=2), req.body_args)

    def test_set_location_specified_new(self):
        """
        Tests the set on the request container
        when the key is not already available and
        the location is specified.
        """
        original_dict = dict(x=1)
        req = RequestContainer(url_params=original_dict)
        req.set('x', 2, QUERY_ARGS)
        self.assertDictEqual(dict(x=2), req.query_args)
        self.assertDictEqual(dict(x=1), req.url_params)

        req = RequestContainer(query_args=original_dict)
        req.set('x', 2, URL_PARAMS)
        self.assertDictEqual(dict(x=2), req.url_params)
        self.assertDictEqual(dict(x=1), req.query_args)

        req = RequestContainer(url_params=original_dict)
        req.set('x', 2, BODY_ARGS)
        self.assertDictEqual(dict(x=2), req.body_args)
        self.assertDictEqual(dict(x=1), req.url_params)
