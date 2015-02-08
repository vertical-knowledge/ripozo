from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import six
from six.moves.urllib import parse
from ripozo.viewsets.constructor import ResourceMetaClass
from ripozo.utilities import classproperty
import re


url_part_finder = re.compile(r'<([^>]+)>')


@six.add_metaclass(ResourceMetaClass)
class ResourceBase(object):
    # TODO class documentation
    __abstract__ = True
    _endpoint_dictionary = None
    _relationships = None
    _pks = None
    _manager = None
    _namespace = None
    _resource_name = None
    _preprocessors = None
    _postprocessors = None

    def __init__(self, properties=None, status_code=200, errors=None, meta=None):
        """
        Initializes a response

        :param dict properties:
        :param int status_code:
        :param list errors:
        :param dict meta:
        """
        if not properties:
            properties = {}
        if not errors:
            errors = []
        if not meta:
            meta = {}
        self.properties = properties
        self.status_code = status_code
        self.errors = errors
        self.meta = meta
        self._url = None

    @property
    def has_error(self):
        return len(self.errors) > 0

    @property
    def url(self):
        """
        Lazily constructs the url for this specific resource using the specific
        pks as specified in the pks tuple.

        :return: The url for this resource
        :rtype: unicode
        """
        if not self._url:
            self._url = create_url(self.base_url, **self.item_pks)
        return self._url

    @property
    def item_pks(self):
        """
        Gets a dictionary of an individual resource's
        primary keys.  The key of the dictionary is the
        name of the primary key and the value is the
        actual value of the primary key specified

        :rtype: dict
        """
        pks = self.pks or []
        pk_dict = {}
        for pk in pks:
            pk_dict[pk] = self.properties.get(pk, None)
        return pk_dict

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
            all_routes.append(dict(route=route, endpoint_func=function, **options))
        cls.endpoint_dictionary[function.__name__] = all_routes

    @classproperty
    def base_url(cls):
        """
        Gets the base_url for the resource
        This is prepended to all routes indicated
        by an apimethod decorator.

        :return: The base_url for the resource(s)
        :rtype: unicode
        """
        pks = cls.pks or []
        parts = list(map(lambda pk: '<{0}>'.format(pk), pks))
        parts.insert(0, cls.resource_name)
        parts.insert(0, re.search(r'(.*)/?$', cls.namespace.strip('/')).group(1))
        base_url = '/'.join(parts)
        return '/{0}'.format(base_url)

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
    def manager(cls):
        return cls._manager()

    @classproperty
    def model_name(cls):
        return cls.manager.model_name

    @classproperty
    def namespace(cls):
        return cls._namespace or ''

    @classproperty
    def pks(cls):
        return cls._pks or []

    @classproperty
    def postprocessors(cls):
        return cls._postprocessors or []

    @classproperty
    def preprocessors(cls):
        return cls._preprocessors or []

    @classproperty
    def relationships(cls):
        return cls._relationships or []

    @classproperty
    def resource_name(cls):
        """
        The resource name for this Resource class
        returns resource_name if not None
        Otherwise it returns the model_name

        :return: The name of the resource for this class
        :rtype: unicode
        """
        if cls._resource_name:
            return cls._resource_name
        return cls.model_name


def create_url(base_url, **kwargs):
    # TODO docstring
    for key, value in six.iteritems(kwargs):
        to_replace = '<{0}>'.format(key)
        base_url = re.sub(to_replace, six.text_type(value), base_url)
    return base_url