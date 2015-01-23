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
    # TODO class documentation
    manager = None
    _endpoint_dictionary = None
    resource_name = None
    relationships = None

    def __init__(self, properties=None, status_code=200, errors=None, meta=None):
        """
        Initializes a response

        :param dict properties:
        :param int status_code:
        :param list errors:
        :param dict meta:
        """
        self.properties = properties or {}
        self.status_code = status_code
        self.errors = errors or []
        self.meta = meta or {}
        if len(errors) == 0:
            self.has_error = False
        else:
            self.has_error = True


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
        for route, endpoint, options in function.routes:
            route = route.lstrip('/')
            route = parse.urljoin(cls.base_url, route)
            all_routes.append(dict(route=route, **options))
        cls.endpoint_dictionary[function.func_name] = all_routes

    @classproperty
    def base_url(cls):
        """
        Gets the base_url for the resource
        This is prepended to all routes indicated
        by an api_method decorator.  Pluralized
        indicates whether more than one resource of the
        type for this method is being acted upon.

        :return: The base_url for the resource(s)
        :rtype: unicode
        """
        pks = cls.pks or []
        return parse.urljoin(cls.namespace, cls._resource_name,
                             *map(lambda pk: '<{0}>'.format(pk), pks))

    @classproperty
    def _manager(cls):
        return cls.manager()