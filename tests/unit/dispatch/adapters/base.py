from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six

from ripozo.dispatch.adapters.contructor import AdapterMeta
from ripozo.dispatch.adapters.base import AdapterBase
from tests.python2base import TestBase

__author__ = 'Tim Martin'


class TestAdapter(AdapterBase):
    __abstract__ = True

    def get_formatted_body(self):
        pass

    def extra_headers(self):
        pass


class TestAdapterBase(TestBase):
    def tearDown(self):
        AdapterMeta.formats = None

    def test_registered_adapter(self):
        class T(TestAdapter):
            formats = ['something']
        self.assertIn('something', six.iterkeys(AdapterMeta.formats))
        self.assertEqual(AdapterBase.formats['something'], T)

    def test_registered_adapter_multiple_formats(self):
        class T2(TestAdapter):
            formats = ['one', 'two', 'three']
        for f in T2.formats:
            self.assertIn(f, six.iterkeys(AdapterBase.formats))
            self.assertEqual(AdapterBase.formats[f], T2)