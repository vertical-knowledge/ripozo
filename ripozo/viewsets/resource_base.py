from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re

from collections import namedtuple

from six.moves.urllib import parse
from ripozo.decorators import classproperty
from ripozo.viewsets.constructor import ResourceMetaClass
from ripozo.utilities import convert_to_underscore, join_url_parts

import inspect
import logging
import six

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

    def __init__(self, properties=None, errors=None, meta=None,
                 status_code=200, query_args=None, include_relationships=True):
        """
        Initializes a response

        :param dict properties:
        :param int status_code:
        :param list errors:
        :param dict meta:
        :param bool include_relationships: If not True, then this resource
            will not include relationships or links.  This is primarily used
            to increase performance with linked resources.
        """
        # TODO finish out the docstring
        self.properties = properties or {}
        self.status_code = status_code
        self.errors = errors or []
        self.meta = meta or {}
        self.query_args = query_args or {}
        self._url = None

        if include_relationships:
            self.related_resources = self._generate_links(self.relationships, self.properties)

            meta_links = self.meta.get('links', {}).copy()
            self.linked_resources = self._generate_links(self.links, meta_links)
        else:
            self.related_resources = []
            self.linked_resources = []

    @staticmethod
    def _generate_links(relationship_list, links_properties):
        """
        Generates a list of linked resources from the links_dict.

        :param list links_dict:
        :param dict links_properties:
        :return: A list of ResourceBase objects
        :rtype: list
        """
        # TODO need much better testing for this
        links = []
        relationship_list = relationship_list or []
        for relationship in relationship_list:
            res = relationship.construct_resource(links_properties)
            if res is None:
                continue
            links.append(_RelatedTuple(res, relationship.name, relationship.embedded))
        return links

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
        base_url = join_url_parts(cls.base_url_sans_pks, *parts).lstrip('/')
        return '/{0}'.format(base_url)

    @classproperty
    def base_url_sans_pks(cls):
        """
        A class property that eturns the base url
        without the pks.
        This is just the /{namespace}/{resource_name}

        For example if the _namespace = '/api' and
        the _resource_name = 'resource' this would
        return '/api/resource' regardless if there
        are pks or not.

        :return: The base url without the pks
        :rtype: unicode
        """
        base_url = join_url_parts(cls.namespace, cls.resource_name).lstrip('/')
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
    def links(cls):
        """
        This should be overridden in __abstract__
        subclasses that require default links such
        as the Create rest mixin.

        :return: A tuple of the links for this class
        :rtype: tuple
        """
        return cls._links or ()

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
        """
        This should be overridden in __abstract__
        classes that require a default relationship.
        For example, you have a series of classes that
        should have an ``user`` relationship.  In that
        case you would simply append the User relationship
        to the _relationships attribute.

        :return: A tuple of the relationships for this class
        :rtype: tuple
        """
        return cls._relationships or ()

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
            base_url = cls.base_url_sans_pks if options.get('no_pks', False) else cls.base_url
            route = join_url_parts(base_url, route)
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
    for name, obj in inspect.getmembers(cls, predicate=_apimethod_predicate):
        yield name, getattr(cls, name)


def _apimethod_predicate(obj):
    return getattr(obj, 'rest_route', False) or getattr(obj, '__rest_route__', False)


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


_RelatedTuple = namedtuple('_RelatedTuple', 'resource, name, embedded')
