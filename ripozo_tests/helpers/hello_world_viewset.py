from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import apimethod, translate
from ripozo.resources.relationships.relationship import Relationship
from ripozo.resources.fields.common import StringField
from ripozo.resources.resource_base import ResourceBase
from ripozo.resources.constructor import ResourceMetaClass
from ripozo_tests.helpers.inmemory_manager import InMemoryManager


class MM1(InMemoryManager):
    model = 'Something'
    _model_name = 'modelname'

name_space = '/mynamspace/'

def get_helloworld_viewset():
    class HelloWorldViewset(ResourceBase):
        _namespace = name_space
        _manager = MM1
        _resource_name = 'myresource'
        _relationships = [
            Relationship('related', property_map={'related': 'id'}, relation='ComplimentaryViewset')
        ]
        _fields = ['content']

        @apimethod(methods=['GET'])
        @translate(fields=[StringField('content')], validate=True)
        def hello(cls, request, *args, **kwargs):
            return cls(properties=request.query_args)
    return HelloWorldViewset


def get_complementary_viewset():
    class ComplimentaryViewset(ResourceBase):
        _namespace = name_space
        _manager = MM1
        _resource_name = 'other_resource'
        _pks = ['id']
    return ComplimentaryViewset


def get_refreshed_helloworld_viewset():
    ResourceMetaClass.registered_names_map = {}
    ResourceMetaClass.registered_resource_classes = {}
    HelloWorldViewset = get_helloworld_viewset()
    ComplimentaryViewset = get_complementary_viewset()
    return HelloWorldViewset