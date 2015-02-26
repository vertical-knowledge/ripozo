from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
import unittest

from ripozo.dispatch.adapters.base import AdapterBase
from ripozo_tests.python2base import TestBase

__author__ = 'Tim Martin'


class TestAdapter(AdapterBase):
    __abstract__ = True

    def get_formatted_body(self):
        pass

    def extra_headers(self):
        pass


class TestAdapterBase(TestBase, unittest.TestCase):
    pass