from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.html import HtmlAdapter
from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.hello_world_viewset import HelloWorldViewset

import unittest


class TestHtmlAdapter(TestBase, unittest.TestCase):
    def setUp(self):
        self.resource = HelloWorldViewset.hello({}, {'content': 'hello'}, {})
        self.adapter = HtmlAdapter(self.resource, base_url='http://localhost:5000/')
        self.response = self.adapter.formatted_body

    def test_fake(self):
        pass
