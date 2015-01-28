__author__ = 'Tim Martin'
from rest.managers.base import NotFoundException
from functools import wraps
from flask import jsonify, url_for
import logging
import json

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
            try:
                response = f(instance, *args, **kwargs)
            except NotFoundException, e:
                response = jsonify(dict(error=True, message=e.message))
                response.status_code = 404

            if instance.postprocessors is not None:
                for function in instance.postprocessors:
                    logger.debug('Running postprocessor: {0}'.format(str(function)))
                    function(response, instance, *args, **kwargs)
            return response

        wrapped.rest_route = True
        if getattr(f, 'routes', None) is None:
            wrapped.routes = []
        else:
            wrapped.routes = getattr(f, 'routes')
        wrapped.routes.append((self.route, self.endpoint, self.options))
        return classmethod(wrapped)


def siren(_f):
    @wraps(_f)
    def wrapped(instance, *args, **kwargs):
        logger = logging.getLogger(__name__)
        response = _f(instance, *args, **kwargs)
        properties = json.loads(response.data)
        code = response.status_code
        js = {
            'class': [instance.__class__.__name__],
            'properties': properties,
            'actions': []
        }

        for m, title in http_methods.iteritems():
            func = getattr(instance, m, None)
            if func is not None:
                action = {}
                action['name'] = title.replace(' ', '-')
                action['title'] = title
                action['method'] = m.upper()
                action['href'] = url_for(instance.endpoint)
                if m in form_methods:
                    action['type'] = 'application/json'
                else:
                    action['type'] = 'application/x-www-form-urlencoded'
                js['actions'].append(action)

        for f, route, options in instance.routed_methods():
            method = options.get('methods', ['GET'])
            method = method[0].upper()
            action = {
                'name': f.__name__,
                'method': method,
                'href': url_for(instance.get_custom_route_endpoint(f)),
            }
            js['actions'].append(action)
        response = jsonify(js)
        response.status_code = code
        if code not in range(200, 300):
            logger.info('The api is returning a non-200 code of {0}'.format(code))
        return response
    return wrapped


def rest_route(route, **options):
    def decorator(f):
        f.custom_route = True
        if getattr(f, 'routes', None) is None:
            f.routes = []
        f.routes.append((route, options, ))
        return f
    return decorator


def accept_custom_routes(cls):
    to_iterate = dict(cls.__dict__)
    for name, method in to_iterate.iteritems():
        if getattr(method, 'rest_route', False) is True:
            for route, options in getattr(method, 'routes'):
                cls.add_routed_method(method, route, **options)
    return cls