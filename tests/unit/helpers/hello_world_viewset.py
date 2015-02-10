from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import apimethod
from ripozo.viewsets.relationship import Relationship
from ripozo.viewsets.resource_base import ResourceBase
from tests.unit.helpers.inmemory_manager import InMemoryManager


class MM1(InMemoryManager):
    model = 'Something'
    _model_name = 'modelname'

name_space = '/mynamspace/'


class HelloWorldViewset(ResourceBase):
    _namespace = name_space
    _manager = MM1
    _resource_name = 'myresource'
    _relationships = {
        'relationship': Relationship(property_map={'related': 'id'}, relation='ComplimentaryViewset')
    }
    _fields = ['content']

    @apimethod(methods=['GET'])
    def hello(cls, primary_keys, filters, values, *args, **kwargs):
        return cls(properties={'content': 'hello', 'related': 'world'})


class ComplimentaryViewset(ResourceBase):
    _namespace = name_space
    _manager = MM1
    _resource_name = 'other_resource'
    _pks = ['id']