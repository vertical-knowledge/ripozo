from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from rest.decorators import apimethod
from rest.viewsets.resource_base import ResourceBase
from tests.unit.helpers.inmemory_manager import InMemoryManager
__author__ = 'Tim Martin'


class MM1(InMemoryManager):
    model = 'Something'
    _model_name = 'modelname'

name_space = '/mynamspace/'


class HelloWorldViewset(ResourceBase):
    __resource_name__ = 'myresource'
    __manager__ = MM1
    namespace = name_space

    @apimethod(methods=['GET'])
    def hello(cls, primary_keys, filters, values, *args, **kwargs):
        return cls(properties={'content': 'hello'})