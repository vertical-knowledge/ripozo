from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.resources.restmixins import CRUDL
from ripozo import fields, RequestContainer
from ripozo.adapters import SirenAdapter, HalAdapter, BoringJSONAdapter

from ripozo_tests.helpers.inmemory_manager import InMemoryManager
from ripozo_tests.helpers.profile import profileit

import logging
import six
import unittest2

class TestRestMixinProfile(unittest2.TestCase):
    runs = 10000

    def setUp(self):
        logging.disable('DEBUG')

        class MyManager(InMemoryManager):
            _fields = ('id', 'first', 'second',)
            _field_validators = {
                'first': fields.IntegerField('first', required=True),
                'second': fields.IntegerField('second', required=True)
            }

        class MyClass(CRUDL):
            resource_name = 'myresource'
            manager = MyManager()

        self.resource_class = MyClass
        self.manager = MyClass.manager
        for i in six.moves.range(100):
            self.manager.objects[i] = dict(id=i, first=1, second=2)
        self.resource = MyClass.retrieve_list(RequestContainer())

    @profileit
    def test_siren_adapter_formatted_body(self):
        adapter = SirenAdapter(self.resource)
        for i in six.moves.range(self.runs):
            x = adapter.formatted_body

    @profileit
    def test_hal_adapter_formatted_body(self):
        adapter = HalAdapter(self.resource)
        for i in six.moves.range(self.runs):
            x = adapter.formatted_body

    # @profileit
    # def test_json_adapter_formatted_body(self):
    #     adapter = BoringJSONAdapter(self.resource)
    #     for i in range(self.runs):
    #         x = adapter.formatted_body
