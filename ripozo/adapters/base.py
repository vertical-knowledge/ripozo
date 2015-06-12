from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import ABCMeta, abstractproperty

from ripozo.utilities import join_url_parts

import json
import six


@six.add_metaclass(ABCMeta)
class AdapterBase(object):
    """
    The adapter base is responsible for specifying how
    a resource should be translated for the client.  For
    example, you may want to specify a specific hypermedia
    protocol or format it in a manner that is specific to
    your client (though you should probably avoid that)

    :param list formats: A list of strings that indicate which Content-Types
        will match with this adapter.  For example, you might include
        'application/vnd.siren+json' in the formats for a SIREN adapter.
        This means that any request with that content type will be responded
        to in the appropriate manner.  Any of the strings in the list will be
        considered the appropriate format for the adapter on which they are
        specified.
    """
    formats = None

    def __init__(self, resource, base_url=''):
        """
        Simple sets the resource on the instance.

        :param resource: The resource that is being formatted.
        :type resource: rest.viewsets.resource_base.ResourceBase
        """
        self.base_url = base_url
        self.resource = resource

    @abstractproperty
    def formatted_body(self):
        """
        This property is the fully qualified and formatted response.
        For example, you might return a Hypermedia formatted response
        body such as the SIREN hypermedia protocol or HAL

        :return: The formatted response body.
        :rtype: unicode
        """
        raise NotImplementedError

    @abstractproperty
    def extra_headers(self):
        """
        Headers that should be added to response.  For example it might be
        the response-type etc...

        :return: A dictionary of the headers to return.
        :rtype: dict
        """
        raise NotImplementedError

    def combine_base_url_with_resource_url(self, resource_url):
        """
        Does exactly what it says it does.  Uses ``join_url_parts``
        with the ``self.base_url`` and ``resource_url`` argument
        together.

        :param unicode resource_url: The part to join with the ``self.base_url``
        :return: The joined url
        :rtype: unicode
        """
        return join_url_parts(self.base_url, resource_url)

    @classmethod
    def format_exception(cls, exc):
        """
        Takes an exception and appropriately formats
        the response.  By default it just returns a json dump
        of the status code and the exception message.
        Any exception that does not have a status_code attribute
        will have a status_code of 500.

        :param Exception exc: The exception to format.
        :return: A tuple containing: response body, format,
            http response code
        :rtype: tuple
        """
        # TODO test
        status_code = getattr(exc, 'status_code', 500)
        return json.dumps(dict(status=status_code, message=six.text_type(exc))), cls.formats[0], status_code

    @property
    def status_code(self):
        """
        :return: Returns the status code of the resource if
            it is available. If it is not it assumes a 200.
        :rtype: int
        """
        return self.resource.status_code or 200
