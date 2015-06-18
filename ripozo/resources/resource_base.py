from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re

from collections import namedtuple

from six.moves.urllib import parse
from ripozo.decorators import classproperty
from ripozo.resources.constructor import ResourceMetaClass
from ripozo.utilities import convert_to_underscore, join_url_parts

import inspect
import logging
import six

logger = logging.getLogger(__name__)


url_part_finder = re.compile(r'<([^>]+)>')


@six.add_metaclass(ResourceMetaClass)
class ResourceBase(object):
    """
    ResourceBase makes up the core of ripozo.  This is the class
    responsible for actually handling requests and appropriately
    constructing resources to return as a request.  This class
    is not responsible for actually formatting the response, only
    for providing a standard resource that can be translated into
    the appropriate response by an adapter.

    The @apimethod decorated methods are the endpoints that will
    be exposed in the api.  @apimethod's are classmethods that generally
    perform some action (such as updating a resource) and then generate
    instances of the class representing that resource.  They take the
    class and a RequestContainer object as the arguments.

    A minimal example would be

    .. code-block:: python

        class MyResource(ResourceBase):
            @apimethod()
            def hello_world(cls, request):
                return cls(properties=dict(hello='world'))


    :param bool __abstract__: abstract classes are not registered
        by the ResourceMetaClass.  In other words, their @apimethod
        decorated methods will not be exposed unless another class
        inherits from it.  __abstract__ is not inherited.
    :param list _relationships: The relationships that will be
        constructed by instances.  The actual related resources
        will be contained in the instances related_resources list.
    :param list pks: The pks for this resource.  These, along
        with the ``namespace`` and ``resource_name`` are combined
        to generate the base url for the class.
    :param ManagerBase manager: The BaseManager subclass that is responsible
        for persistence within the applictation.  I.E. the AlchemyManager
        from ripozo-sqlalchemy
    :param unicode namespace: The namespace of this resource.  This is
        prepended to the resource_name and pks to create the url
    :param unicode resource_name: The name of the resource.
    :param list preprocessors: A list of functions that will be run before
        any apimethod is called.
    :param list postprocessors: A list of functions that will be run after
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
    pks = tuple()
    manager = None
    namespace = '/'
    preprocessors = tuple()
    postprocessors = tuple()
    _links = None

    def __init__(self, properties=None, errors=None, meta=None, no_pks=False,
                 status_code=200, query_args=None, include_relationships=True):
        """
        Initializes a resource to pass to an adapter typically.
        An ResourceBase instance is supposed to fully represent the
        resource.

        :param dict properties: The properties on
        :param int status_code: The http status code that should be returned
        :param list errors: A list of error that occurred.  Typically not used.
        :param dict meta: Meta information about the resource (for example
            the next page in a paginated list)
        :param bool no_pks: Whether the resource should have primary keys
            or not.  Helpful when returning a list of resources for example.
        :param bool include_relationships: If not True, then this resource
            will not include relationships or links.  This is primarily used
            to increase performance with linked resources.
        :param list|tuple query_args: A list of the arguments that should
            be appended to the query string if necessary.
        :param bool include_relationships:  This flag is available to prevent
            infinite loops in resources that each have a relationship to
            the other.
        """
        # TODO finish out the docstring
        self.properties = properties or {}
        self.status_code = status_code
        self.errors = errors or []
        self.meta = meta or {}
        self.query_args = query_args or {}
        self._url = None
        self.no_pks = no_pks

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
        """
        :return: Whether or not the instance has an error
        :rtype: bool
        """
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

    def get_query_arg_dict(self):
        """
        :return: Gets the query args that are available
            in the properties.  This allows the user
            to quickly get the query args out.
        :rtype: dict
        """
        queries = {}
        for field in self.query_args:
            value = self.properties.get(field)
            if value is not None:
                queries[field] = value
        return queries

    @property
    def query_string(self):
        """
        :return: The generated query string for this resource
        :rtype: str|unicode
        """
        return '&'.join('{0}={1}'.format(f, v) for f, v in self.get_query_arg_dict().items())

    @property
    def url(self):
        """
        Lazily constructs the url for this specific resource using the specific
        pks as specified in the pks tuple.

        :return: The url for this resource
        :rtype: unicode
        """
        if not self._url:
            base_url = self.base_url_sans_pks if self.no_pks else self.base_url
            url = create_url(base_url, **self.item_pks)
            query_string = self.query_string
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
        return convert_to_underscore(cls.__name__)


def _generate_endpoint_dict(cls):
    """
    Generates a dictionary of the endpoints on the class
    which are @apimethod decorated.

    :param ResourceMetaClass cls: The ResourceBase subclass that you
        are trying to get the endpoints from.
    :type cls:
    :return:
    :rtype:
    """
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

    :param ResourceMetaClass cls: The instance of a ResourceMetaClass
        that you wish to retrieve the apimethod decorated methods
        from.
    :type cls:
    :return: A generator for tuples of the name, method combo
    :rtype: type.GeneratorType
    """
    for name, obj in inspect.getmembers(cls, predicate=_apimethod_predicate):
        yield name, getattr(cls, name)


def _apimethod_predicate(obj):
    """
    The predicate for determining if the object
    is an @apimethod decorated method.

    :param object obj: The object to check
    :return: A bool indicating if the object
        was an @apimethod decorated method.
    :rtype: bool
    """
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
