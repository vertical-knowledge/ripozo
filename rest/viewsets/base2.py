from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import types

__author__ = 'Tim Martin'


class ResourceMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        klass = super(ResourceMetaClass, mcs).__new__(mcs, name, bases, attrs)

        for key, value in attrs.iteritems():
            if isinstance(value, types.FunctionType) and value.rest_route is True:
                klass.register_endpoint(value)
        return klass