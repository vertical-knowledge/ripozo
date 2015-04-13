from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re

import six

from six.moves.urllib import parse
from ripozo.decorators import classproperty
from ripozo.viewsets.constructor import ResourceMetaClass
from ripozo.viewsets.relationships import Relationship, ListRelationship
from ripozo.utilities import convert_to_underscore, join_url_parts

import inspect
import logging

logger = logging.getLogger(__name__)


url_part_finder = re.compile(r'<([^>]+)>')


@six.add_metaclass(ResourceMetaClass)
class ResourceBase(object):
    """
    The core of ripozo.

    :param bool __abstract__: abstract classes are not registered
        by the ResourceMetaClass
    :param dict _relationships: The relationships that will be
        constructed by instances
    :param list _pks: The pks for this resource.  These, along
        with the ``namespace`` and ``resource_name`` are combined
        to generate the url
    :param type _manager: The BaseManager subclass that is responsible
        for persistence within the applictation.  I.E. the AlchemyManager
        from ripozo-sqlalchemy
    :param unicode _namespace: The namespace of this resource.  This is
        prepended to the resource_name and pks to create the url
    :param unicode _resource_name: The name of the resource.
    :param list _preprocessors: A list of functions that will be run before
        any apimethod is called.
    :param list _postprocessors: A list of functions that will be run after
        any apimethod from this class is called.
    :param dict _links: Works similarly to relationships.  The primary
        difference between this and links is that links will assume the
        resource is the same as this class if a relation is not specified.
        Additionally, links are supposed to be meta information effectively.
        They are not necessarily about this specific resource.  For example,
        next and previous links for a list resource or created links when
        creating a new resource on a list resource.
    """

    __abstract__ = True
    _relationships = None
    _pks = None
    _manager = None
    _namespace = '/'
    _resource_name = None
    _preprocessors = None
    _postprocessors = None
    _links = None

    def __init__(self, properties=None, errors=None, meta=None, status_code=200, query_args=None, embedded=False):
        """
        Initializes a response

        :param dict properties:
        :param int status_code:
        :param list errors:
        :param dict meta:
        """
        properties = properties or {}
        errors = errors or []
        meta = meta or {}
        self.properties = properties
        self.status_code = status_code
        self.errors = errors
        self.meta = meta
        self.query_args = query_args or {}
        self._url = None
        self._relationships = self._relationships or {}

        relationships = {}
        for field_name, relationship in six.iteritems(self._relationships):
            relationship_list = []
            for related_resource in relationship.construct_resource(self.properties):
                relationship_list.append((related_resource, relationship.embedded,))
            self.properties = relationship.remove_child_resource_properties(self.properties)
            relationships[field_name] = relationship_list
        self.relationships = relationships

        links = []
        meta_links = self.meta.get('links', {}).copy()
        for name, value in six.iteritems(self.meta.get('links', {})):
            existing_links = self._links or {}
            if name in existing_links:
                link = existing_links[name]
            elif isinstance(value, list):
                link = ListRelationship(name, relation=self.__class__.__name__)
            else:
                link = Relationship(name=name, relation=self.__class__.__name__)
            query_args = meta_links.get(link.name, {}).pop('query_args', {})
            for res in link.construct_resource(meta_links, query_args=query_args):
                links.append((link.name, res,))
        self.links = links

    @property
    def has_error(self):
        return len(self.errors) > 0 or self.status_code >= 400

    @property
    def has_all_pks(self):
        """
        :return: Indicates whether an instance of this class
            has all of the items in the pks list as a key in
            the ``self.properties`` attribute.
        :rtype: bool
        """
        # TODO test
        for pk in self.pks:
            if pk not in self.properties:
                return False
        return True

    @property
    def url(self):
        """
        Lazily constructs the url for this specific resource using the specific
        pks as specified in the pks tuple.

        :return: The url for this resource
        :rtype: unicode
        """
        if not self._url:
            url = create_url(self.base_url, **self.item_pks)
            query_string = '&'.join('{0}={1}'.format(x, y) for x, y in six.iteritems(self.query_args))
            if query_string:
                url = '{0}?{1}'.format(url, query_string)
            self._url = url
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
    """
    A generator that yields tuples of the name and method of
    all ``@apimethod`` decorated methods on the class.

    :param type cls: The instance of a ResourceMetaClass
        that you wish to retrieve the apimethod decorated methods
        from.
    :type cls:
    :return: A generator for tuples of the name, method combo
    :rtype: type.GeneratorType
    """
    for name, obj in inspect.getmembers(cls):
        if getattr(obj, 'rest_route', False) or getattr(obj, '__rest_route__', False):
            # Need to use getattr so that __get__ is appropriately called.
            yield name, getattr(cls, name)


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