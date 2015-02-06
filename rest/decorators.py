__author__ = 'Tim Martin'
from functools import wraps
import logging

http_methods = {
    'get': 'Retrieve',
    'post': 'Add',
    'put': 'Edit idempotent',
    'patch': 'Edit',
    'delete': 'Delete',
    'head': 'Head',
    'options': 'Options'
}

form_methods = ['post', 'put', 'patch']


class apimethod(object):
    """
    Decorator for declaring routes on a rest resource
    """
    def __init__(self, route='', endpoint=None, **options):
        """
        Hold on to the arguments for the decorator to append to the class map
        """
        logger = logging.getLogger(__name__)
        logger.info('Initializing apimethod route: {0} with options {1}'.format(route, options))
        self.route = route
        self.options = options
        self.endpoint = endpoint

    def __call__(self, f):
        # TODO: add documentation here

        logger = logging.getLogger(__name__)

        @wraps(f)
        def wrapped(instance, *args, **kwargs):
            return f(instance, *args, **kwargs)

        wrapped.rest_route = True
        if getattr(f, 'routes', None) is None:
            wrapped.routes = []
        else:
            wrapped.routes = getattr(f, 'routes')
        wrapped.routes.append((self.route, self.endpoint, self.options))
        return classmethod(wrapped)