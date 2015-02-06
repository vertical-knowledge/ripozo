from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from unittest import TestCase
__author__ = 'Tim Martin'


class TestBase(TestCase):
    def assertIn(self, member, container, msg=None):
        self.assertTrue(member in container, msg=msg)

    def assertIsInstance(self, obj, cls, msg=None):
        self.assertTrue(isinstance(obj, cls), msg=msg)
