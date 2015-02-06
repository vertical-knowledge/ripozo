from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from unittest import TestCase


import difflib
import pprint

from unittest.util import safe_repr
__author__ = 'Tim Martin'


class TestBase(TestCase):
    def assertIn(self, member, container, msg=None):
        self.assertTrue(member in container, msg=msg)

    def assertIsInstance(self, obj, cls, msg=None):
        self.assertTrue(isinstance(obj, cls), msg=msg)

    def assertDictEqual(self, d1, d2, msg=None):
        self.assertIsInstance(d1, dict, 'First argument is not a dictionary')
        self.assertIsInstance(d2, dict, 'Second argument is not a dictionary')

        if d1 != d2:
            standardMsg = '%s != %s' % (safe_repr(d1, True), safe_repr(d2, True))
            diff = ('\n' + '\n'.join(difflib.ndiff(
                           pprint.pformat(d1).splitlines(),
                           pprint.pformat(d2).splitlines())))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))
