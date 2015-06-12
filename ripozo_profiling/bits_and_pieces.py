from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.utilities import convert_to_underscore

from ripozo_tests.helpers.profile import profileit

import six
import unittest2


class TestBitsAndPieces(unittest2.TestCase):
    runs = 1000000

    @profileit
    def test_convert_to_underscore(self):
        for i in six.moves.range(self.runs):
            convert_to_underscore('MyThingYeah')
