"""
The class constructor for resources.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import warnings

_logger = logging.getLogger(__name__)


class ResourceMetaClass(type):
    """
    A metaclass that is used for registering ResourceBase
    and its subclasses  It is primarily responsible
    for creating a registry of the available Resources
    so that they can map relationships and links.

    :param dict registered_resource_classes: A dictionary mapping
        the classes instantiated by this meta class to their
        base_urls
    :param dict registered_names_map:  A dictionary mapping the names
        of the classes to the actual instances of this meta class
    """
    registered_resource_classes = {}
    registered_names_map = {}
    registered_resource_names_map = {}

    def __new__(mcs, name, bases, attrs):
        """
        The instantiator for the metaclass.  This
        is responsible for creating the actual class
        itself.

        :return: The class
        :rtype: type
        """
        _logger.debug('ResourceMetaClass "%s" class being created', name)
        klass = super(ResourceMetaClass, mcs).__new__(mcs, name, bases, attrs)
        if attrs.get('__abstract__', False) is True:  # Don't register endpoints of abstract classes
            _logger.debug('ResourceMetaClass "%s" is abstract.  Not being registered', name)
            return klass
        mcs.register_class(klass)

        _logger.debug('ResourceMetaClass "%s" successfully registered', name)
        return klass

    @classmethod
    def register_class(mcs, klass):
        """
        Checks if the class is in the registry
        and adds it to the registry if the classes base_url
        is not in it.  Otherwise it raises a BaseRestEndpointAlreadyExists
        exception so as not to offer multiple endpoints for the same base_url

        :param klass: The class to register
        :raises: BaseRestEndpointAlreadyExists
        """
        mcs.registered_resource_classes[klass] = klass.base_url
        if klass.__name__ in mcs.registered_names_map:
            warnings.warn('A class with the name {0} has already been registered.'
                          'Overwriting that class'.format(klass.__name__), UserWarning)
        mcs.registered_names_map[klass.__name__] = klass
        resource_name = getattr(klass, 'resource_name', klass.__name__)
        mcs.registered_resource_names_map[resource_name] = klass
