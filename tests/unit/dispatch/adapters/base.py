from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from rest.dispatch.adapters.contructor import AdapterMeta
from rest.dispatch.adapters.base import AdapterBase
import unittest
__author__ = 'Tim Martin'


class TestAdapter(AdapterBase):
    __abstract__ = True

    def get_formatted_body(self):
        pass

    def extra_headers(self):
        pass


class TestAdapterBase(unittest.TestCase):
    def tearDown(self):
        AdapterMeta.formats = None

    def test_registered_adapter(self):
        class T(TestAdapter):
            formats = ['something']
        self.assertIn('something', AdapterMeta.formats.keys())
        self.assertEqual(AdapterBase.formats['something'], T)

    def test_registered_adapter_multiple_formats(self):
        class T2(TestAdapter):
            formats = ['one', 'two', 'three']
        for f in T2.formats:
            self.assertIn(f, AdapterBase.formats.keys())
            self.assertEqual(AdapterBase.formats[f], T2)