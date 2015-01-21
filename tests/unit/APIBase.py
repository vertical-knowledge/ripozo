__author__ = 'Tim Martin'
import unittest
from rest.viewsets.base import APIBase
from werkzeug.routing import Map


class TestAPIBase(unittest.TestCase):
    def test_get_url_map(self):
        base = APIBase()
        base_map = base.url_map
        self.assertIsInstance(base_map, Map)
        base_map_2 = base.url_map
        self.assertEqual(base_map, base_map_2)

    def test_get_routed_methods(self):
        base = APIBase()
        routed_methods = base.routed_methods
        self.assertIsInstance(routed_methods, list)
        routed2 = base.routed_methods
        self.assertEqual(routed_methods, routed2)
        routed2.append('something')
        self.assertEqual(routed_methods, routed2)
        self.assertListEqual(routed2, routed_methods)

    def test_generated_route_endpoint(self):
        def my_function():
            return
        endpoint = APIBase.get_custom_route_endpoint(my_function)
        self.assertIsInstance(endpoint, unicode)
        self.assertIn(my_function.__name__, endpoint)