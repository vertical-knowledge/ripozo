from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps, update_wrapper

import logging
import six


class ClassPropertyDescriptor(object):
    """
    Straight up stolen from stack overflow
    Implements class level properties
    http://stackoverflow.com/questions/5189699/how-can-i-make-a-class-property-in-python
    """

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()


def classproperty(func):
    """
    Using this decorator a class can have a decorator. Necessary for dynamically settings urls
    on application/blueprint

    :param func: The function to wrap
    :type func: function
    :rtype: ClassPropertyDescriptor
    """
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassPropertyDescriptor(func)


class _apiclassmethod(object):
    __name__ = str('_apiclassmethod')

    def __init__(self, f):
        update_wrapper(self, f)
        for key, value in six.iteritems(getattr(f, 'func_dict', {})):
            self.__dict__[key] = value

        self.f = f
        if hasattr(f, 'func_name'):
            self.func_name = f.func_name

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)

        @wraps(self.f)
        def newfunc(*args):
            if len(args) == 0 or not isinstance(args[0], type):
                return self.f(klass, *args)
            return self.f(*args)
        return newfunc

    def __call__(self, cls, *args, **kwargs):
        return self.__get__(None, klass=cls)(*args, **kwargs)


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

        In addition to setting some properties on the function itself
        (i.e. ``__rest_route__`` and ``routes``), It also wraps the actual
        function calling both the preprocessors and postprocessors.

        preprocessors get at least the cls, name of the function, request as arguments

        postprocessors get the cls, function name, request and resource as arguments

        :param classmethod f:
        :return: The wrapped classmethod that is an action
            that can be performed on the resource.  For example,
            any sort of CRUD action.
        :rtype: classmethod
        """
        setattr(f, '__rest_route__', True)
        routes = getattr(f, 'routes', [])
        routes.append((self.route, self.endpoint, self.options))
        setattr(f, 'routes', routes)

        @_apiclassmethod
        @wraps(f)
        def wrapped(cls, request, *args, **kwargs):
            for proc in cls.preprocessors:
                proc(cls, f.__name__, request, *args, **kwargs)
            resource = f(cls, request, *args, **kwargs)
            for proc in cls.postprocessors:
                proc(cls, f.__name__, request, resource, *args, **kwargs)
            return resource
        return wrapped


class translate(object):
    """
    Decorator for validating the inputs to an apimethod
    and describing what is allowed for that apimethod to
    an adapter if necessary.
    """

    def __init__(self, fields=None, manager_field_validators=False, skip_required=False, validate=False):
        """
        Initializes the decorator with the necessary fields.
        the fields should be instances of FieldBase and should
        give descriptions of the parameter and how to input them
        (i.e. query or body parameter)

        :param list fields: A list of FieldBase instances (or subclasses
            of FieldBase).
        :param bool manager_field_validators: A flag that indicates the
            field_validators property on the BaseManager subclass that
            is registered on the ResourceBase subclass that this method
            is a part of.
        :param bool skip_required: If this flag is set to True,
            then required fields will be considered optional.
        :param bool validate: Indicates whether the validations should
            be run.  If it is False, it will only translate the fields.
        """
        self.original_fields = fields or []
        self.manager_field_validators = manager_field_validators
        self.skip_required = skip_required
        self.validate = validate
        self.cls = None

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
        @_apiclassmethod
        @wraps(f)
        def action(cls, request, *args, **kwargs):
            # TODO This is so terrible.  I really need to fix this.
            request.translate(self.fields(cls.manager), skip_required=self.skip_required, validate=self.validate)
            return f(cls, request,  *args, **kwargs)

        action.__manager_field_validators__ = self.manager_field_validators
        action.fields = self.fields
        return action

    def fields(self, manager):
        if self.manager_field_validators:
            return self.original_fields + manager.field_validators
        return self.original_fields