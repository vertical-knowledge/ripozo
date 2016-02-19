"""
The RequestContainer.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import warnings

import six
from six.moves import urllib

from ripozo.resources.constants import input_categories

_LOG = logging.getLogger(__name__)


class _Headers(dict):
    """"
    A case insensitive dictionary for headers.
    Includes a helper factory method ``from_wsgi_environ``
    for easy construction from a wsgi environ object
    """
    def __setitem__(self, key, value):
        """
        Case insensitive set item method

        :param unicode key:
        :param unicode value:
        """
        super(_Headers, self).__setitem__(key.title(), value)

    def __getitem__(self, key):
        """
        Case insensitive __getitem__ implementation

        :param unicode key:
        :rtype: unicode
        """
        return super(_Headers, self).__getitem__(key.title())

    @classmethod
    def from_wsgi_environ(cls, environ):
        """
        Constructs a Headers dictionary from
        a wsgi environ object

        :param dict environ: The wsgi environ object
        :type environ:
        :return: A case insentive dictionary of valid headers
        :rtype: _Headers
        """
        headers = cls()
        for key, value in six.iteritems(environ):
            if key.startswith('HTTP_'):
                key = key[5:]
                key = key.replace('_', '-')
                headers[key] = value
            if key in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
                key = key.replace('_', '-')
                headers[key] = value
        return headers


def _parse_form_encoded(form_encoded_string):
    """
    Safely parses a form encoded string.  Starting
    in ripozo v2.0.0 bad query strings will raise an
    Exception

    :param unicode form_encoded_string:
    :return: The parsed values from the string
    :rtype: dict
    """
    try:
        return urllib.parse.parse_qs(form_encoded_string,
                                     keep_blank_values=True,
                                     strict_parsing=True)
    except ValueError as e:
        warnings.warn('The query string "{0}" is invalid.  In '
                      'ripozo v2.0.0 this will raise a ValidationException. '
                      'Error Message: {1}'.format(form_encoded_string, e),
                      DeprecationWarning)
        return urllib.parse.parse_qs(form_encoded_string,
                                     keep_blank_values=True,
                                     strict_parsing=False)


def _parse_query_string(environ):
    """
    Retrieves the query string from the wsgi
    environ object and returns the parsed values

    :param dict environ: The wsgi environ
    :return: The parsed values from the query string
    :rtype: dict
    """
    query_string = environ.get('QUERY_STRING', '')
    return _parse_form_encoded(query_string)


def _parse_body(environ):
    """
    Parse the request body by first attempting to load it
    as JSON and then trying to parse it as a form encoded
    string

    :param dict environ: The wsgi environ dictionary
    :return: The parsed body
    :rtype: dict
    """
    raw_body_file = environ.get('wsgi.input')
    raw_body = raw_body_file.read() if raw_body_file else None
    if not raw_body:
        return {}

    try:
        return json.loads(raw_body)
    except ValueError:
        return _parse_form_encoded(raw_body)


class RequestContainer(object):
    """
    An object that represents an incoming request.
    This is done primarily to keep the data in one
    place and to make a generically accessible object.
    It should be assumed that no parameter is required
    and no property is guaranteed.
    """

    def __init__(self, url_params=None, query_args=None, body_args=None, headers=None, method=None, environ=None):
        """
        Create a new request container.  Typically this is constructed
        in the dispatcher.

        :param dict url_params: The url parameters that are a part of the
            request.  These are the variable parts of the url.  For example,
            a request with /resource/<id> would have the id as a url_param
        :param dict query_args: The query args are were in the request.  They
            should be a adictionary
        :param dict body_args: The arguments in the body.
        :param dict headers: A dictionary of the headers and their values
        :param unicode method: The method that was used to make
            the request.
        """
        self._url_params = url_params or {}
        self._query_args = query_args or {}
        self._body_args = body_args or {}
        self._headers = headers or {}
        self.environ = environ or {}
        self.method = method

    @classmethod
    def from_wsgi_environ(cls, environ, url_params):
        headers = _Headers.from_wsgi_environ(environ)
        query_args = _parse_query_string(environ)
        body_args = _parse_body(environ)
        return cls(
            headers=headers,
            query_args=query_args,
            body_args=body_args,
            url_params=url_params,
            method=environ['REQUEST_METHOD'],
            environ=environ
        )

    @property
    def url_params(self):
        """
        :return: A copy of the url_params dictionary
        :rtype: dict
        """
        return self._url_params.copy()

    @url_params.setter
    def url_params(self, value):
        self._url_params = value

    @property
    def query_args(self):
        """
        :return: A copy of the query_args
        :rtype: dict
        """
        return self._query_args.copy()

    @query_args.setter
    def query_args(self, value):
        self._query_args = value

    @property
    def body_args(self):
        """
        :return: a copy of the body_args
        :rtype: dict
        """
        return self._body_args.copy()

    @body_args.setter
    def body_args(self, value):
        self._body_args = value

    @property
    def headers(self):
        """
        :return: A copy of the headers dict
        :rtype: dict
        """
        return self._headers.copy()

    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def content_type(self):
        """
        :return: The Content-Type header or None if it is not available in
            the headers property on this request object.
        :rtype: unicode
        """
        return self._headers.get('Content-Type')

    @content_type.setter
    def content_type(self, value):
        self._headers['Content-Type'] = value

    def get(self, name, default=None, location=None):
        """
        Attempts to retrieve the parameter with the
        name in the url_params, query_args and then
        body_args in that order.  Returns the default
        if not found.

        :param unicode name: The name of the parameter
            to retrieve. From the request
        :return: The requested attribute if found
            otherwise the default if specified.
        :rtype: object
        :raises: KeyError
        """
        if (not location and name in self._url_params) or location == input_categories.URL_PARAMS:
            return self.url_params.get(name)
        elif (not location and name in self._query_args) or location == input_categories.QUERY_ARGS:
            return self._query_args.get(name)
        elif (not location and name in self._body_args) or location == input_categories.BODY_ARGS:
            return self._body_args.get(name, default)
        return default

    def set(self, name, value, location=None):
        """
        Attempts to set the field with the specified name.
        in the location specified.  Searches through all
        the fields if location is not specified.  Raises
        a KeyError if no location is set and the name is
        not found in any of the locations.

        :param unicode name: The name of the field
        :param unicode location: The location of the
            field to get. I.e. QUERY_ARGS.
        :return: The field that was requestedor None.
        :rtype: object
        """
        if not location and name in self._url_params or location == input_categories.URL_PARAMS:
            self._url_params[name] = value
            return
        elif not location and name in self._query_args or location == input_categories.QUERY_ARGS:
            self._query_args[name] = value
            return
        elif not location and name in self._body_args or location == input_categories.BODY_ARGS:
            self._body_args[name] = value
            return
        raise KeyError('Location was not specified and the parameter {0} '
                       'could not be found on the request object'.format(name))

    def __contains__(self, item):
        """
        Checks if the item is available in any of
        the url_params, body_args, or query_args

        :param unicode item: The key to look for in the
            various parameter dictionaries.
        :return: Whether the object was actually found.
        :rtype: bool
        """
        if item in self._url_params or item in self._body_args or item in self._query_args:
            return True
        return False
