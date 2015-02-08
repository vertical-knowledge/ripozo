from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal

import re
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

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


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


_first_cap_re = re.compile('(.)([A-Z][a-z]+)')
_all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert_to_underscore(toconvert):
    """
    Converts a string from CamelCase to underscore

    :param toconvert: The string to convert from CamelCase to underscore (i.e. camel_case)
    :type toconvert: str
    :return: The converted string
    :rtype: str
    """
    i = 0
    while toconvert[i] == '_':
        i += 1
    prefix = None
    if i > 0:
        prefix = toconvert[0:i]
        toconvert = toconvert[i:]
    s1 = _first_cap_re.sub(r'\1_\2', toconvert)
    s2 = _all_cap_re.sub(r'\1_\2', s1).lower()
    if prefix is not None:
        return '{0}{1}'.format(prefix, s2)
    return s2


def make_json_serializable(value):
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S.%f')
    elif isinstance(value, set):
        return list(value)
    else:
        return value
        raise ValueError('A boolean value accepted as a string must be either "true" or "false"')


def serialize_fields(field_names, field_values):
    """
    Takes two lists and iterates through them to combine them into a dictionary

    :param field_names: The names of the fields that were retrieved.  Order is important.
      These will be the dictionary keys
    :type field_names: list
    :param field_values: The values that were retrieved. These will be the dictionary values
    :type field_values: list
    :return: A dictionary of the combined lists
    :rtype: dict
    """
    dictified = {}
    field_values = iter(field_values)
    for i, name in enumerate(field_names):
        dictified[name] = make_json_serializable(six.next(field_values))
    return dictified


def titlize_endpoint(endpoint):
    """
    Capitalizes the endpoint and makes it look like a title
    Just to prettify the output of the actions.  It capitalizes
    the first letter of every word and replaces underscores with
    spaces.  It is opinionated in how it determines words.  It
    simply looks for underscores and splits based on that.

    :param unicode endpoint: The endpoint name on the resource
    :return: The prettified endpoint name
    :rtype: unicode
    """
    parts = endpoint.split('_')
    parts = (p.capitalize() for p in parts)
    endpoint = ' '.join(parts)
    return endpoint.strip()