from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import BaseRestEndpointAlreadyExists

import logging
import inspect
import six

logger = logging.getLogger(__name__)


# TODO the metaclass requires knowledge of the class... Maybe this shouldn't be so?
# TODO documentation on class and __new__
class ResourceMetaClass(type):
    """
    :param dict registered_resource_classes: TODO
    """
    registered_resource_classes = {}
    registered_names_map = {}

    def __new__(mcs, name, bases, attrs):
        logger.debug('ResourceMetaClass "{0}" class being created'.format(name))
        klass = super(ResourceMetaClass, mcs).__new__(mcs, name, bases, attrs)
        if attrs.get('__abstract__', False):  # Don't register endpoints of abstract classes
            logger.debug('ResourceMetaClass "{0}" is abstract.  Not being registered'.format(name))
            return klass

        mcs._register_endpoints(klass)
        mcs._register_class(klass)

        logger.debug('ResourceMetaClass "{0}" successfully registered'.format(name))
        return klass

    @classmethod
    def _register_endpoints(mcs, klass):
        """
        Finds all methods that have been marked with the
        rest_route indicator.  It then uses the classes register_endpoint
        method to register the endpoints appropriately.  This is done to
        avoid accidentally registering methods that are not ripozo
        endpoints.

        :param klass: The class to register endpoints on.
        """
        for name, method in inspect.getmembers(klass, inspect.ismethod):
            if getattr(method, 'rest_route', False):
                logger.debug('Registering method {0} as a valid '
                             'action on resource {1}'.format(method.__name__, klass.__name__))
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
        if klass.base_url in six.itervalues(mcs.registered_resource_classes):
            raise BaseRestEndpointAlreadyExists
        mcs.registered_resource_classes[klass] = klass.base_url
        mcs.registered_names_map[klass.__name__] = klass