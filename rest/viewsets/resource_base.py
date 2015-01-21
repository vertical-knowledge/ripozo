from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import six
from six.moves.urllib import parse
from rest.viewsets.base2 import ResourceMetaClass
from rest.utilities import classproperty

__author__ = 'Tim Martin'


@six.add_metaclass(ResourceMetaClass)
class ResourceBase(object):
    _endpoint_dictionary = None
    resource_name = None
    pluralization = None

    @classproperty
    def endpoint_dictionary(cls):
        """
        A dictionary of the endpoints with the
        method as the key and the route options as the
        value

        :return: dictionary of endpoints
        :rtype: dict
        """
        if cls._endpoint_dictionary is None:
            cls._endpoint_dictionary = {}
        return cls._endpoint_dictionary

    @classproperty
    def _pluralization(cls):
        """
        The pluralization for this Resource.
        Checks if one has been explicitly declared and returns that if so.
        Otherwise, it simply appends and "s" to the resource_name/model_name

        :return: The pluralized name for the resource on this class
        :rtype: unicode
        """
        if cls.pluralization:
            return cls.pluralization
        return '{0}s'.format(cls._resource_name)

    @classproperty
    def _resource_name(cls):
        """
        The resource name for this Resource class
        returns resource_name if not None
        Otherwise it returns the model_name

        :return: The name of the resource for this class
        :rtype: unicode
        """
        if cls.resource_name:
            return cls.resource_name
        return cls.model_name

    @classmethod
    def register_endpoint(cls, function):
        """
        Registers a method as an exposed endpoint.
        Any method decorated with @api_method will
        be registered via this method.  Additionally,
        There must be a parameter on the method call "routes"
        This is a list that indicates which routes should point
        to this method.  Typically only one route should point

        :param function: The method to register as an endpoint
        :type function: types.FunctionType
        """
        all_routes = []
        for route, endpoint, options, pluralized in function.routes:
            route = route.lstrip('/')
            route = parse.urljoin(cls.get_base_url(pluralized=pluralized), route)
            all_routes.append(dict(route=route, **options))
        cls.endpoint_dictionary[function.func_name] = all_routes

    @classmethod
    def get_base_url(cls, pluralized=False):
        """
        Gets the base_url for the resource
        This is prepended to all routes indicated
        by an api_method decorator.  Pluralized
        indicates whether more than one resource of the
        type for this method is being acted upon.

        :param bool pluralized: Indicates whether more than one resource is being acted upon
        :return: The base_url for the resource(s)
        :rtype: unicode
        """
        if pluralized:
            secondary = cls._pluralization
        elif cls.resource_name:
            secondary = cls.resource_name
        else:
            secondary = cls.model_name
        if cls.pks and len(cls.pks) != 0 and not pluralized:
            return parse.urljoin(cls.namespace, secondary, *map(lambda pk: '<{0}>'.format(pk), cls.pks))
        return parse.urljoin(cls.namespace, secondary)