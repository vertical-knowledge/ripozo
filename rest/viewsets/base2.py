from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from rest.exceptions import BaseRestEndpointAlreadyExists

import types

__author__ = 'Tim Martin'


class ResourceMetaClass(type):
    registered_resource_classes = {}

    def __new__(mcs, name, bases, attrs):
        klass = super(ResourceMetaClass, mcs).__new__(mcs, name, bases, attrs)

        for key, value in attrs.iteritems():
            if isinstance(value, types.FunctionType) and value.rest_route is True:
                klass.register_endpoint(value)
        mcs._register_class(klass)
        return klass

    def _register_class(cls, klass):
        """
        Checks if the class is in the registry
        and adds it to the registry if the classes base_url
        is not in it.  Otherwise it raises a BaseRestEndpointAlreadyExists
        exception so as not to offer multiple endpoints for the same base_url

        :param type klass: The class to register
        :raises: BaseRestEndpointAlreadyExists
        """
        if klass.base_url in cls.registered_resource_classes.values():
            raise BaseRestEndpointAlreadyExists
        cls.registered_resource_classes[klass] = klass.base_url