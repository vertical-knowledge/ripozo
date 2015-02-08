from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
from ripozo.dispatch.adapters.contructor import AdapterMeta
from ripozo.dispatch.adapters.siren import SirenAdapter
from ripozo.viewsets.constructor import ResourceMetaClass
import six


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

    def register_class_routes(self, klass):
        """
        Register a subclass of the ResourceBase on the framework
        implementation.  This is so that the actual actions on the
        resources can be dispatched to by the framework.

        :param type klass: The class whose endpoints must be registered
        """
        for endpoint, routes in six.iteritems(klass.endpoint_dictionary):
            for options in routes:
                options = options.copy()
                route = options.pop('route', klass.base_url)
                methods = options.pop('methods', ['GET'])
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
        result = endpoint_func(*args, **kwargs)
        adapter_class = AdapterMeta.formats.get(format_type)
        adapter = adapter_class(result)
        return adapter