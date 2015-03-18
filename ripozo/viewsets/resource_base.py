from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re

import six

from six.moves.urllib import parse
from ripozo.viewsets.constructor import ResourceMetaClass
from ripozo.viewsets.constants import status
from ripozo.utilities import classproperty, convert_to_underscore, join_url_parts

import inspect
import logging

logger = logging.getLogger(__name__)


url_part_finder = re.compile(r'<([^>]+)>')


@six.add_metaclass(ResourceMetaClass)
class ResourceBase(object):
    # TODO class documentation
    __abstract__ = True
    _endpoint_dictionary = None
    _relationships = None
    _pks = None
    _manager = None
    _namespace = '/'
    _resource_name = None
    _preprocessors = None
    _postprocessors = None

    def __init__(self, properties=None, errors=None, meta=None, status=None):
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
        self.status = status
        self.errors = errors
        self.meta = meta
        self._url = None

    @property
    def has_error(self):
        return len(self.errors) > 0 or self.status == status.ERRORED

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
        parts.insert(0, cls.namespace)
        base_url = join_url_parts(*parts).lstrip('/')
        return '/{0}'.format(base_url)

    @classmethod
    def endpoint_dictionary(cls):
        """
        A dictionary of the endpoints with the
        method as the key and the route options as the
        value

        :return: dictionary of endpoints
        :rtype: dict
        """
        # TODO update this documentation
        return _generate_endpoint_dict(cls)

    @classproperty
    def manager(cls):
        if cls._manager is None:
            return None
        return cls._manager()

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
        return cls._relationships or {}

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
        return convert_to_underscore(cls.__name__)

def _generate_endpoint_dict(cls):
    # TODO test and doc string
    endpoint_dictionary = {}
    for name, method in _get_apimethods(cls):
        logger.debug('Found the apimethod {0} on the class {1}'.format(name, cls.__name__))
        all_routes = []
        for route, endpoint, options in method.routes:
            route = join_url_parts(cls.base_url, route)
            all_routes.append(dict(route=route, endpoint_func=method, **options))
        logger.info('Registering routes: {0} as key {1}'.format(all_routes, name))
        endpoint_dictionary[name] = all_routes
    return endpoint_dictionary


def _get_apimethods(cls):
    for name, obj in inspect.getmembers(cls):
        if getattr(obj, 'rest_route', False) or getattr(obj, '__rest_route__', False):
            yield name, obj


def create_url(base_url, **kwargs):
    """
    Generates a fully qualified url.  It iterates
    over the keyword arguments and for each key
    it replaces any instances of "<key>" with "value"
    The keys of the dictionary must be strings.

    :param unicode base_url: The url template that will
        be used to generate an acutal url
    :param dict kwargs: The dictionary of template variables
        and their associated values
    :return: A complete url.
    :rtype: unicode
    """
    for key, value in six.iteritems(kwargs):
        to_replace = '<{0}>'.format(key)
        base_url = re.sub(to_replace, six.text_type(value), base_url)
    return base_url