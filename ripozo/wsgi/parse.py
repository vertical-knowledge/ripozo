"""
Utilities for parsing arguments from the query string and body
of requests using the WSGI environ object
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from cgi import parse_header
import json
import warnings

import six
from six.moves import urllib

from ripozo.exceptions import UnreadableBodyException
from ripozo.wsgi.headers import Headers, get_raw_content_type
from ripozo.resources.request import RequestContainer


def parse_form_encoded(form_encoded_string, charset='utf-8'):
    """
    Safely parses a form encoded string.  Starting
    in ripozo v2.0.0 bad query strings will raise an
    Exception

    :param unicode form_encoded_string:
    :param unicode charset: The character set to decode the
        values as.
    :return: The parsed values from the string
    :rtype: dict{unicode: list[unicode]}
    """

    try:
        query_parts = urllib.parse.parse_qs(form_encoded_string,
                                            keep_blank_values=True,
                                            strict_parsing=True)
    except ValueError as e:
        warnings.warn('The query string "{0}" is invalid.  In '
                      'ripozo v2.0.0 this will raise a ValidationException. '
                      'Error Message: {1}'.format(form_encoded_string, e),
                      DeprecationWarning)
        query_parts = urllib.parse.parse_qs(form_encoded_string,
                                            keep_blank_values=True,
                                            strict_parsing=False)

    # Already unicode return as is
    if six.PY3:
        return query_parts

    # Convert to unicode
    unicode_query_parts = {}
    for key, value in six.iteritems(query_parts):
        unicode_query_parts[key.decode(charset)] = [val.decode(charset) for val in value]
    return unicode_query_parts


def _parse_query_string(environ):
    """
    Retrieves the query string from the wsgi
    environ object and returns the parsed values

    :param dict environ: The wsgi environ
    :return: The parsed values from the query string
    :rtype: dict
    """
    query_string = environ.get('QUERY_STRING', '')
    return parse_form_encoded(query_string)


def _get_charset(environ):
    """
    Gets the character set from the wsgi environ
    via the Content-Type header.

    :param dict environ: The WSGI environ object
    :return: The string identifying the character
        set of the request
    :rtype: unicode
    """
    content_type = get_raw_content_type(environ)
    content_type, params = parse_header(content_type)
    return params.get('charset', 'utf-8')


def coerce_body_to_unicode(environ):
    """
    Coerces the request body to unicode using
    the charset from the Content-Type header
    defaulting to utf-8 is the Content-Type header
    is null

    :param dict environ:
    :return: The body as a unicode string
    :rtype: unicode
    :raises: UnreadableBodyException
    """
    raw_body_file = environ.get('wsgi.input')
    raw_body = raw_body_file.read() if raw_body_file else ''

    # Decode the body into unicode
    if not isinstance(raw_body, six.text_type):
        charset = _get_charset(environ)

        try:
            raw_body = raw_body.decode(charset)
        except LookupError:
            raise UnreadableBodyException('unknown charset: "{0}" from'
                                          ' Content-Type header'.format(charset))
        except UnicodeDecodeError:
            raise UnreadableBodyException('The request body cannot be decoded '
                                          'using the charset "{0}" from the Content-Type'
                                          ' header (default=utf-8)'.format(charset))
    return raw_body


def json_loads_backwards_compatible(body, content_type='application/json'):
    """
    This method is a shim to maintain backwards compatibility
    until ripozo v2.0.0 It reads what should be a json string
    as either a JSON string or a form encoded string if that
    fails

    .. deprecated:: 1.3.1
        Use ``json.loads`` instead

    :param body:
    :param content_type:
    :return: The parameters from the body as a dictionary
    :rtype: dict
    """
    if not body:
        return {}
    try:
        return json.loads(body)
    except ValueError:
        warnings.warn('The content type "{0}" only allows for '
                      'json requests bodies.  The automatic handling '
                      'of form encoded bodies will be deprecated in '
                      'ripozo v2.0.0. In the future, an exception '
                      'will be raised and the client will receive a '
                      '4xx response '.format(content_type), DeprecationWarning)
        return parse_form_encoded(body)


def get_http_verb(environ):
    """
    Gets the HTTP Verb (e.g. ``"GET"``, ``"POST"``)
    from the wsgi environ.  It will always be uppercased

    :param dict environ:
    :return: The HTTP method as unicode
    :rtype: unicode
    :raises: KeyError if there is no ``'REQUEST_METHOD'`` in
        the wsgi environ as is expected
    """
    method = environ['REQUEST_METHOD'].upper()
    if not isinstance(method, six.text_type):
        method = method.decode('utf-8')
    return method


def construct_request_from_wsgi_environ(environ, url_parameters, body_parser):
    """
    Constructs a complete request from a wsgi environ.
    It uses the body_parser to parse the unicode request
    body into parameters.  The body_parser should take
    one parameter a unicode string representing the body
    of the request

    :param dict environ: The WSGI environ
    :param dict url_parameters: The url parameters, these
        are usually based on the framework's router and cannot
        be generically parsed.
    :param function body_parser: Should take one unicode argument
        representing the body of the request
    :return: A ripozo native RequestContainer object
    :rtype: RequestContainer
    """
    headers = Headers.from_wsgi_environ(environ)
    query_args = _parse_query_string(environ)
    raw_body = coerce_body_to_unicode(environ)
    body_args = body_parser(raw_body)
    method = get_http_verb(environ)
    return RequestContainer(headers=headers,
                            query_args=query_args,
                            body_args=body_args,
                            url_params=url_parameters,
                            method=method,
                            environ=environ)
