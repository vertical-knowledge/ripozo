from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import inspect

logger = logging.getLogger(__name__)


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

    def __new__(mcs, name, bases, attrs):
        """
        The instantiator for the metaclass.  This
        is responsible for creating the actual class
        itself.

        :return: The class
        :rtype: type
        """
        logger.debug('ResourceMetaClass "{0}" class being created'.format(name))
        klass = super(ResourceMetaClass, mcs).__new__(mcs, name, bases, attrs)
        if attrs.get('__abstract__', False) is True:  # Don't register endpoints of abstract classes
            logger.debug('ResourceMetaClass "{0}" is abstract.  Not being registered'.format(name))
            return klass
        mcs._register_class(klass)

        logger.debug('ResourceMetaClass "{0}" successfully registered'.format(name))
        return klass

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
        mcs.registered_resource_classes[klass] = klass.base_url
        mcs.registered_names_map[klass.__name__] = klass

        # TODO test and doc this
        for name, method in inspect.getmembers(klass):
            if getattr(method, '__manager_field_validators__', False) is True \
                    or getattr(method, 'manager_field_validators', False) is True:
                if not hasattr(method, 'cls'):
                    setattr(method, 'cls', klass)
                    method = classmethod(method)
                    setattr(klass, name, method)
