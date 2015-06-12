from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.resources.restmixins import CRUDL
from ripozo import fields, RequestContainer

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
            manager = MyManager()
            resource_name = 'myresource'

        self.resource_class = MyClass
        self.manager = MyClass.manager

    @profileit
    def test_retrieve(self):
        self.manager.objects['1'] = dict(id='1', first=1, second=2)
        request = RequestContainer(url_params=dict(id='1'))
        for i in six.moves.range(self.runs):
            self.resource_class.retrieve(request)

    @profileit
    def test_retrieve_list(self):
        for i in six.moves.range(100):
            self.manager.objects[i] = dict(id=i, first=1, second=2)
        req = RequestContainer()
        for i in six.moves.range(self.runs):
            self.resource_class.retrieve_list(req)

    @profileit
    def test_create(self):
        req = RequestContainer(body_args=dict(first='1', second='2'))
        for i in six.moves.range(self.runs):
            self.resource_class.create(req)

    @profileit
    def test_update(self):
        self.manager.objects['1'] = dict(id='1', first=1, second=2)
        req = RequestContainer(url_params=dict(id='1'))
        for i in six.moves.range(self.runs):
            req._body_args['first'] = i
            self.resource_class.update(req)

    def test_delete(self):
        ids = six.moves.range(self.runs)
        req = RequestContainer(body_args=dict(first='1', second='2'))
        for i in ids:
            self.manager.objects[i] = dict(id=i, first=1, second=2)
        self.actually_delete(ids)

    @profileit
    def actually_delete(self, ids):
        req = RequestContainer()
        for id_ in ids:
            req._url_params['id'] = id_
            self.resource_class.delete(req)
