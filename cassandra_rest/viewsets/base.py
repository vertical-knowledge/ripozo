__author__ = 'Tim Martin'
from cassandra_rest.utilities import classproperty
from flask import request
from flask.views import View
from werkzeug.routing import Map, Rule
from cassandra_rest.utilities import convert_to_underscore
import inspect
import logging


class APIBase(View):
    manager = None
    preprocessors = None
    postprocessors = None
    pks = None
    _routed_methods_list = None
    _routed_methods_dict = None
    _url_map = None
    paginate_by = 10000
    namespace = u'/api'
    resource_name = None
    pluralization = None

    def __init__(self):
        if not self.pks:
            self.pks = []
        if not self.preprocessors:
            self.preprocessors = []
        if not self.postprocessors:
            self.postprocessors = []
        self.setup_rest_routes()

    @classproperty
    def model(cls):
        return cls.manager.model

    @property
    def model_name(self):
        return convert_to_underscore(self._get_manager().model_name)

    def _get_manager(self):
        return self.manager()

    @property
    def url_map(self):
        if self._url_map is None:
            self._url_map = Map()
        return self._url_map

    @property
    def routed_methods(self):
        if self._routed_methods_list is None:
            self._routed_methods_list = []
        return self._routed_methods_list

    @property
    def routed_methods_dict(self):
        if self._routed_methods_dict is None:
            self._routed_methods_dict = {}
        return self._routed_methods_dict

    def add_routed_method(self, f, route, pluralized=False, endpoint=None, **options):
        if endpoint is None:
            endpoint = self.get_custom_route_endpoint(f)
        self.routed_methods_dict[endpoint] = f
        base_url = self.get_base_url(pluralized=pluralized)
        route = u'{0}{1}'.format(base_url, route)
        self.url_map.add(Rule(route, endpoint=endpoint, **options))
        t = (f, route, options, endpoint)
        self.routed_methods.append(t)

    def dispatch_request(self, *args, **kwargs):
        environ = request.environ
        adapter = self.url_map.bind_to_environ(environ)

        endpoint, values = adapter.match()
        f = self.routed_methods_dict[endpoint]

        self.run_processors(self.preprocessors, extra_args=args, **kwargs)
        response = f(*args, **kwargs)
        self.run_processors(self.postprocessors, response=response, extra_args=args, **kwargs)

        return response

    def setup_rest_routes(self):
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if getattr(method, 'rest_route', False) is True:
                for route, options, pluralized in getattr(method, 'routes'):
                    self.add_routed_method(method, route, pluralized=pluralized, **options)

    def run_processors(self, processors, response=None, extra_args=None, **kwargs):
        """
        Runs the processors. processors should abort or throw an exception if there is an issue
        """
        logger = logging.getLogger(__name__)
        if extra_args is None:
            extra_args = []
        if processors is not None:
            for function in processors:
                logger.debug('Running processor: {0}'.format(str(function)))
                if response:
                    function(response, self, *extra_args, **kwargs)
                else:
                    function(self, *extra_args, **kwargs)

    @classmethod
    def get_custom_route_endpoint(cls, f):
        return '{0}__{1}'.format(cls.__name__, f.__name__)

    def get_base_url(self, pluralized=False):
        if pluralized:
            secondary = self._pluralization
        elif self.resource_name:
            secondary = self.resource_name
        else:
            secondary = self.model_name
        if self.pks and len(self.pks) != 0 and not pluralized:
            return '{0}/{1}/{2}'.format(self.namespace, secondary,
                                        '/'.join(map(lambda pk: '<{0}>'.format(pk), self.pks)))
        return '{0}/{1}'.format(self.namespace, secondary)

    @property
    def _pluralization(self):
        if self.pluralization:
            return self.pluralization
        elif self.resource_name:
            name = self.resource_name
        else:
            name = self.model_name
        return '{0}s'.format(name)


def register_viewset(app, viewset):
    """
    Adds the routes to the application and or blueprint

    :param app: The application or blueprint
    :type app: flask.Flask|flask.Blueprint
    :param viewset: The viewset to register
    :type viewset: class
    """
    # Add routes to flask app/blueprint
    for f, route, options, endpoint in viewset().routed_methods:
        app.add_url_rule(route, view_func=viewset.as_view(endpoint), **options)