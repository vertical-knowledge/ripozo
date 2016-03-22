from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six


class Headers(dict):
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
        if not isinstance(value, six.text_type):
            value = value.decode('utf-8')
        super(Headers, self).__setitem__(key.title(), value)

    def __getitem__(self, key):
        """
        Case insensitive __getitem__ implementation

        :param unicode key:
        :rtype: unicode
        """
        return super(Headers, self).__getitem__(key.title())

    @staticmethod
    def from_wsgi_environ(environ):
        """
        Constructs a Headers dictionary from
        a wsgi environ object

        :param dict environ: The wsgi environ object
        :type environ:
        :return: A case insentive dictionary of valid headers
        :rtype: Headers
        """
        headers = Headers()
        for key, value in six.iteritems(environ):
            if key.startswith('HTTP_'):
                key = key[5:]
                key = key.replace('_', '-')
                headers[key] = value
            if key in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
                key = key.replace('_', '-')
                headers[key] = value
        return headers
