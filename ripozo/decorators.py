from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps
from ripozo.exceptions import RestException
from ripozo.viewsets.constants import input_categories
import logging


class apimethod(object):
    """
    Decorator for declaring routes on a ripozo resource
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
        """
        The actual decorator that will be called and returns the method
        that is a ripozo route.

        :param classmethod f:
        :return: The wrapped classmethod that is an action
            that can be performed on the resource.  For example,
            any sort of CRUD action.
        :rtype: classmethod
        """
        @wraps(f)
        def wrapped(instance, *args, **kwargs):
            return f(instance, *args, **kwargs)

        wrapped.rest_route = True
        wrapped.routes = getattr(f, 'routes', [])
        wrapped.routes.append((self.route, self.endpoint, self.options))
        return classmethod(wrapped)


class validate(object):
    """
    Decorator for validating the inputs to an apimethod
    and describing what is allowed for that apimethod to
    an adapter if necessary.
    """

    def __init__(self, fields=None):
        """
        Initializes the decorator with the necessary fields.
        the fields should be instances of FieldBase and should
        give descriptions of the parameter and how to input them
        (i.e. query or body parameter)

        :param list fields: A list of FieldBase instances (or subclasses
            of FieldBase).
        """
        self.fields = fields or []

    def __call__(self, f):
        """
        Wraps the function with translation and validation.
        This allows the inputs to be cast and validated as necessary.
        Additionally, it provides the adapter with information about
        what is necessary to successfully make a request to the wrapped
        apimethod.

        :param method f:
        :return: The wrapped function
        :rtype: function
        """
        @wraps(f)
        def action(cls, url_params, query_args, body_args, *args, **kwargs):
            for field in self.fields:
                # Translate and validate the inputs
                if field.arg_type == input_categories.URL_PARAMS:
                    url_params[field.name] = field.translate_and_validate(url_params.get(field.name, None))
                elif field.arg_type == input_categories.BODY_ARGS:
                    body_args[field.name] = field.translate_and_validate(body_args.get(field.name, None))
                elif field.arg_type == input_categories.QUERY_ARGS:
                    query_args[field.name] = field.translate_and_validate(query_args.get(field.name, None))
                else:
                    raise RestException('Invalid arg_type, {0}, on Field {1}'.format(field.arg_type, field.name))

            return f(cls, url_params, query_args, body_args, *args, **kwargs)

        action.fields = self.fields
        return action
