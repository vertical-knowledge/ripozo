from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest.exceptions import BaseRestEndpointAlreadyExists

import inspect


# TODO the metaclass requires knowledge of the class... Maybe this shouldn't be so?
# TODO documentation on class and __new__
class ResourceMetaClass(type):
    """
    :param dict registered_resource_classes: TODO
    """
    registered_resource_classes = {}

    def __new__(mcs, name, bases, attrs):
        klass = super(ResourceMetaClass, mcs).__new__(mcs, name, bases, attrs)
        if attrs.get('__abstract__', False):  # Don't register endpoints of abstract classes
            return klass

        mcs._register_endpoints(klass)
        mcs._register_class(klass)
        return klass

    @classmethod
    def _register_endpoints(mcs, klass):
        """
        Finds all methods that have been marked with the
        rest_route indicator.  It then uses the classes register_endpoint
        method to register the endpoints appropriately.  This is done to
        avoid accidentally registering methods that are not rest
        endpoints.

        :param klass: The class to register endpoints on.
        """
        for name, method in inspect.getmembers(klass, inspect.ismethod):
            if getattr(method, 'rest_route', False):
                klass.register_endpoint(method)

    @classmethod
    def _register_class(mcs, klass):
        """
        Checks if the class is in the registry
        and adds it to the registry if the classes base_url
        is not in it.  Otherwise it raises a BaseRestEndpointAlreadyExists
        exception so as not to offer multiple endpoints for the same base_url

        :param klass: The class to register
        :raises: BaseRestEndpointAlreadyExists
        """
        if klass.base_url in mcs.registered_resource_classes.values():
            raise BaseRestEndpointAlreadyExists
        mcs.registered_resource_classes[klass] = klass.base_url