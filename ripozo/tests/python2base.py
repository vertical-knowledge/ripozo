from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Tim Martin'


class TestBase(object):
    def assertIn(self, member, container, msg=None):
        self.assertTrue(member in container, msg=msg)

    def assertIsInstance(self, obj, cls, msg=None):
        self.assertTrue(isinstance(obj, cls), msg=msg)

    def assertDictEqual(self, d1, d2, msg=None):
        self.assertIsInstance(d1, dict, 'First argument is not a dictionary')
        self.assertIsInstance(d2, dict, 'Second argument is not a dictionary')
        self.assertTrue(d1 == d2, msg=msg)

    def assertIsNotNone(self, obj, msg=None):
        self.assertTrue(obj is not None, msg=msg)

    def assertIsNone(self, obj, msg=None):
        self.assertTrue(obj is None, msg=msg)

    def assertLessEqual(self, a, b, msg=None):
        self.assertTrue(a <= b, msg=msg)

    def assertListEqual(self, a, b, msg=None):
        for i in range(len(a)):
            self.assertEqual(a[i], b[i], msg=msg)
