from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
from ripozo.dispatch.adapters.base import AdapterBase
from ripozo.exceptions import AdapterFormatAlreadyRegisteredException

import logging
import six

logger = logging.getLogger(__name__)


@six.add_metaclass(ABCMeta)
class DispatcherBase(object):
    """
    This is an abstract base class that is responsible
    for handling the interface between a request and
    the resource as well as the interface between the
    resource and the response.  A new subclass should be
    developed for every framework that ripozo is supposed
    to work with.  Those extensions should be in separate
    repositories though.  This specific base class is
    mostly for shortcuts and to give an idea of how to
    actually implement ripozo with a framework.
    """
    _adapter_formats = None
    _default_adapter = None

    @property
    def adapter_formats(self):
        """
        Returns the mutable _adapter_formats.
        If the _adapter_formats property is None
        then it first sets cls._adapter_formats to an
        empty dictionary.

        :rtype: dict
        """
        if self._adapter_formats is None:
            self._adapter_formats = {}
        return self._adapter_formats

    @abstractproperty
    def base_url(self):
        """
        :return: The base url including the domain and protocol
            This needs to be included so that the adapters
            can construct fully qualified urls.  However, they
            have no way of directly identifying that so they
            need to be able to get it from the dispatcher.
        :rtype: unicode
        """
        pass

    @property
    def default_adapter(self):
        """
        :return: The AdapterBase subclass that is the default
            adapter to use when the client doesn't explicitly request
            a specific adapter.  If no default adapter is set when
            register_adapters is called, then the first adapter provided
            to register_adapters will be set as the default adapter.
        :rtype: AdapterBase
        """
        return self._default_adapter

    @default_adapter.setter
    def default_adapter(self, adapter_class):
        """
        Sets the default adapter to use when the client
        does not explicitly ask for a certain adapter type.

        :param type adapter_class: the class to use as the default
            adapter class
        """
        logger.info('Setting the default adapter for a Dispatcher as {0}'.format(adapter_class))
        self._default_adapter = adapter_class

    def register_adapters(self, *adapter_classes):
        """
        Registers a list of valid adapter classes with this dispatcher.
        It will take the formats attribute from the AdapterBase subclass
        and use each of those as a key with the value pointing.

        If _default_adapter is not set, then the first adapter_class
        will be the default adapter to use when returning responses.

        :param list adapter_classes: A list of subclasses of AdapterBase
            that specify what formats are available for this dispatcher
        :raises: AdapterFormatAlreadyRegisteredException
        """
        if len(adapter_classes) > 0 and self.default_adapter is None:
            self.default_adapter = adapter_classes[0]
        for klass in adapter_classes:
            for format in klass.formats:
                if format in self.adapter_formats or format is None:
                    raise AdapterFormatAlreadyRegisteredException('The format {0} has already been registered'
                                                                  ' for the class {1}.  The class {2} was attempting'
                                                                  ' to override '
                                                                  'it.'.format(format,
                                                                               self.adapter_formats[format].__name__,
                                                                               klass.__name__))
                logger.debug('Registering format {0} to be hanlded by the AdapterBase'
                             ' subclass {1}'.format(format, klass))
                self.adapter_formats[format] = klass

    def register_resources(self, *classes):
        """
        A shortcut for register multiple classes at once.

        :param list classes: A list of ResourceBase subclasses that are being
            registered with this dispatcher.
        """
        for klass in classes:
            self.register_class_routes(klass)

    def register_class_routes(self, klass):
        """
        Register a subclass of the ResourceBase on the framework
        implementation.  This is so that the actual actions on the
        resources can be dispatched to by the framework.

        :param ripozo.viewsets.resource_base.ResourceBase klass: The
            class whose endpoints must be registered
        """
        for endpoint, routes in six.iteritems(klass.endpoint_dictionary()):
            endpoint = '{0}.{1}'.format(klass.__name__, endpoint)
            for options in routes:
                options = options.copy()
                route = options.pop('route', klass.base_url)
                methods = options.pop('methods', ['GET'])
                logger.info('Registering the endpoint {0} to handle route {1}'
                            ' with the methods {2} on a DispatcherBase '
                            'subclass'.format(endpoint, route, methods))
                self.register_route(endpoint, route=route, methods=methods, **options)

    @abstractmethod
    def register_route(self, endpoint, endpoint_func=None, route=None, methods=None, **options):
        """
        Registers an individual route on the framework.  This method
        gives a specific framework the opportunity to actually dispatch
        the incoming requests appropriately.

        :param unicode endpoint: The name of the endpoint
        :param method endpoint_func: The endpoint_func that is responsible
            for actually performing the actions requested
        :param unicode route: The route template for this endpoint
        :param list methods: A list of the methods on this route that
            will point to the endpoint_funct
        :param dict options: A dictionary of additional options.
        """
        pass

    def dispatch(self, endpoint_func, format_type, *args, **kwargs):
        """
        A helper to dispatch the endpoint_func, get the ResourceBase
        subclass instance, get the appropriate AdapterBase subclass
        and return an instance created with the ResourceBase.

        :param method endpoint_func: The endpoint_func is responsible
            for actually get the ResourceBase response
        :param unicode format_type: The format_type for the response
            format that should be returned.
        :param list args: a list of args that wll be passed
            to the endpoint_func
        :param dict kwargs: a dictionary of keyword args to
            pass to the endpoint_func
        :return: an instance of an AdapterBase subclass that
            can be used to find
        :rtype:
        """
        logger.info('Dispatching request to endpoint function: {0} with args:'
                    ' {1} and kwargs: {2}'.format(endpoint_func, args, kwargs))
        result = endpoint_func(*args, **kwargs)
        adapter_class = self.get_adapter_for_type(format_type)
        logger.info('Using adapter {0} to format response for format'
                    ' type {1}'.format(adapter_class, format_type))
        adapter = adapter_class(result, base_url=self.base_url)
        return adapter

    def get_adapter_for_type(self, format_type):
        """
        Gets the appropriate adapter class for the specified format
        type.  For example, if the format_type was siren it would
        return the SirenAdapter.  Returns the default adapter
        If it cannot not find an adapter for the format_type.

        :param unicode format_type:
        :return:
        :rtype: type
        """
        return self.adapter_formats.get(format_type, self.default_adapter)