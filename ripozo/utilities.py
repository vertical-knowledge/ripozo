from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps

import datetime
import decimal
import re
import six


_first_cap_re = re.compile('(.)([A-Z][a-z]+)')
_all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert_to_underscore(toconvert):
    """
    Converts a string from CamelCase to underscore.

    .. code-block:: python

        >>> convert_to_underscore('CamelCase')
        'camel_case'

    :param toconvert: The string to convert from CamelCase to underscore (i.e. camel_case)
    :type toconvert: str
    :return: The converted string
    :rtype: str
    """
    s1 = _first_cap_re.sub(r'\1_\2', toconvert)
    return _all_cap_re.sub(r'\1_\2', s1).lower()


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


def join_url_parts(*parts):
    """
    Joins each of the parts with a '/'.
    Additionally, it prevents something like 'something/' and
    '/another' from turning into 'something//another' instead
    it will return 'something/another'.

    .. code-block:: python

        >>> join_url_parts('first', 'second', 'last')
        'first/second/last'

    :param list parts: a list of strings to join together with a '/'
    :return: The url
    :rtype: unicode
    """
    url = None
    if len(parts) == 0:
        return ''
    for part in parts:
        if url is None:  # first case
            url = part
            continue
        url = url.rstrip('/')
        part = part.lstrip('/')
        url = '{0}/{1}'.format(url, part)
    return url


def picky_processor(processor, include=None, exclude=None):
    """
    A wrapper for pre and post processors that selectively runs
    pre and post processors.  If the include keyword argument is set,
    then any method on the Resource that has the same name as the
    processor will be run.  Otherwise it will not be run.  On the
    other hand, if the exclude keyword argument is set then any
    method on then this preprocessor will not be run for any method on
    the resource that does have the same name as the strings in the
    exclude list

    .. code-block:: python

        def my_preprocessor(resource_class, func_name, request):
            # Do something

        class MyResource(CRUD):
            # Only gets run on create and delete
            _preprocessors = [picky_processor(my_preprocessor, include=['create', 'delete'])]

    :param method processor: A pre or post processor on a ResourceBase subclass.
        This is the function that will be run if the it passes the include
        and exclude parameters
    :param list include: A list of name strings that are methods on the class that
        for which this processor will be run.
    :param list exclude:
    :return: The wrapped function that only runs if the include and
        exclude parameters are fulfilled.
    :rtype: method
    """
    @wraps(processor)
    def wrapped(cls, function_name, *args, **kwargs):
        run = True
        if include and function_name not in include:
            run = False
        elif exclude and function_name in exclude:
            run = False
        if run:
            return processor(cls, function_name, *args, **kwargs)
    return wrapped


def make_json_safe(obj):
    """
    Makes an object json serializable.
    This is designed to take a list or dictionary,
    and is fairly limited.  This is primarily for
    the managers when creating objects.

    :param object obj:
    :return: The json safe dictionary.
    :rtype: object|six.text_type|list|dict
    """
    if isinstance(obj, dict):
        for key, value in six.iteritems(obj):
            obj[key] = make_json_safe(value)
    elif isinstance(obj, (list, set, tuple,)):
        response = []
        for val in obj:
            response.append(make_json_safe(val))
        return response
    elif isinstance(obj, (datetime.datetime, datetime.date, datetime.time, datetime.timedelta)):
        obj = six.text_type(obj)
    elif isinstance(obj, decimal.Decimal):
        obj = float(obj)
    return obj
