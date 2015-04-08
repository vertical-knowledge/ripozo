from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.fields.base import translate_fields


class RequestContainer(object):
    """
    An object that represents an incoming request.
    This is done primarily to keep the data in one
    place and to make a generically accessible object.
    It should be assumed that no parameter is required
    and no property is guaranteed.
    """

    def __init__(self, url_params=None, query_args=None, body_args=None, headers=None, method=None):
        """
        Safely generate a Request object.  There should be reasonable defaults
        for every parameter.  No parameter is guaranteed.

        :param dict url_params: The url parameters that are a part of the
            request.  These are the variable parts of the url.  For example,
            a request with /resource/<id> would have the id as a url_param
        :param dict query_args: The query args are were in the request.  They
            should be a adictionary
        :param dict body_args: The arguments in the body.
        :param dict headers: A dictionary of the headers and their values
        """
        self._url_params = url_params or {}
        self._query_args = query_args or {}
        self._body_args = body_args or {}
        self._headers = headers or {}
        self.method = method

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
        return self._headers.get('Content-Type', None)

    @content_type.setter
    def content_type(self, value):
        self._headers['Content-Type'] = value

    def translate(self, fields, skip_required=False, validate=False):
        """
        TODO
        :param list fields:
        """
        self._url_params, self._query_args, self._body_args = translate_fields(
            self._url_params, self._query_args, self._body_args,
            fields=fields, validate=validate, skip_required=skip_required
        )
