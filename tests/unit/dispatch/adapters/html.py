from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.html import HtmlAdapter
from ripozo.viewsets.request import RequestContainer
from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.hello_world_viewset import get_refreshed_helloworld_viewset

import unittest


class TestHtmlAdapter(TestBase, unittest.TestCase):
    def setUp(self):
        HelloWorldViewset = get_refreshed_helloworld_viewset()
        self.resource = HelloWorldViewset.hello(RequestContainer(query_args=dict(content='hello',
                                                                                 related='world')))
        self.adapter = HtmlAdapter(self.resource, base_url='http://localhost:5000/')
        self.response = self.adapter.formatted_body

    def test_extra_headers(self):
        adapter = HtmlAdapter(None)
        self.assertEqual(adapter.extra_headers, {'Content-Type': 'text/html'})
