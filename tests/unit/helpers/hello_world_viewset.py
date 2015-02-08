from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from ripozo.decorators import apimethod
from ripozo.viewsets.resource_base import ResourceBase
from tests.unit.helpers.inmemory_manager import InMemoryManager
__author__ = 'Tim Martin'


class MM1(InMemoryManager):
    model = 'Something'
    _model_name = 'modelname'

name_space = '/mynamspace/'


class HelloWorldViewset(ResourceBase):
    namespace = name_space
    _manager = MM1
    _resource_name = 'myresource'

    @apimethod(methods=['GET'])
    def hello(cls, primary_keys, filters, values, *args, **kwargs):
        return cls(properties={'content': 'hello'})