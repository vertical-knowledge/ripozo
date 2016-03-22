"""
Boring json which is just a basic
dump of the resource into json format.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial
import json
from warnings import warn

import six

from ripozo.adapters import AdapterBase
from ripozo.wsgi.parse import construct_request_from_wsgi_environ, json_loads_backwards_compatible

_CONTENT_TYPE = 'application/json'
_json_loads_backwards_compatible = partial(json_loads_backwards_compatible, content_type=_CONTENT_TYPE)


class BasicJSONAdapter(AdapterBase):
    """
    Just a plain old JSON dump of the properties.
    Nothing exciting.

    Format:

    .. code-block:: javascript

        <resource_name>: {
            field1: "value"
            field2: "value"
            relationship: {
                relationship_field: "value"
            }
            list_relationship: [
                {
                    relationship_field: "value"
                }
                {
                    relationship_field: "value"
                }
            ]
        }
    """
    formats = ['json', _CONTENT_TYPE]
    extra_headers = {'Content-Type': _CONTENT_TYPE}

    @property
    def formatted_body(self):
        """
        :return: The formatted body that should be returned.
            It's just a ``json.dumps`` of the properties and
            relationships
        :rtype: unicode
        """
        response = dict()
        parent_properties = self.resource.properties.copy()
        self._append_relationships_to_list(response, self.resource.related_resources)
        self._append_relationships_to_list(response, self.resource.linked_resources)
        response.update(parent_properties)
        return json.dumps({self.resource.resource_name: response})

    @staticmethod
    def _append_relationships_to_list(rel_dict, relationships):
        """
        Dumps the relationship resources provided into
        a json ready list of dictionaries.  Side effect
        of updating the dictionary with the relationships

        :param dict rel_dict:
        :param list relationships:
        :return: A list of the resources in dictionary format.
        :rtype: list
        """
        for resource, name, embedded in relationships:
            if name not in rel_dict:
                rel_dict[name] = []
            if isinstance(resource, (list, tuple)):
                for res in resource:
                    rel_dict[name].append(res.properties)
                continue
            rel_dict[name].append(resource.properties)

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
        status_code = getattr(exc, 'status_code', 500)
        body = json.dumps(dict(status=status_code, message=six.text_type(exc)))
        return body, cls.formats[0], status_code

    @classmethod
    def format_request(cls, request):
        """
        Simply returns request

        .. deprecated:: 1.3.1
            format_request has been deprecated in favor of
            `construct_request_from_wsgi_environ` it will be
            removed in v2.0.0

        :param RequestContainer request: The request to handler
        :rtype: RequestContainer
        """
        warn('`format_request` has been deprecated in favor of '
             '`construct_request_from_wsgi_environ` it will be'
             ' removed in v2.0.0',
             PendingDeprecationWarning)
        return request

    @classmethod
    def construct_request_from_wsgi_environ(cls, environ, url_params):
        """
        Parses a request and appropriately constructs a RequestContainer
        representing it.

        :param dict environ: The WSGI environ object.  A dictionary
            like object that almost all python web frameworks use
            based on `PEP 3333 <https://www.python.org/dev/peps/pep-3333/>`_
        :return: A ripozo ready RequestContainer object representing
            the request
        :rtype: RequestContainer
        """
        return construct_request_from_wsgi_environ(
            environ,
            url_params,
            _json_loads_backwards_compatible
        )
