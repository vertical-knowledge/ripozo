"""
HAL adapter.  See `HAL Specification <http://stateless.co/hal_specification.html>`_
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from functools import partial
from warnings import warn

import six

from ripozo.adapters import AdapterBase
from ripozo.wsgi.parse import json_loads_backwards_compatible, construct_request_from_wsgi_environ

_CONTENT_TYPE = 'application/hal+json'
_json_loads_backwards_compatible = partial(json_loads_backwards_compatible, content_type=_CONTENT_TYPE)


class HalAdapter(AdapterBase):
    """
    An adapter that formats the response in the HAL format.
    A description of the HAL format can be found here:
    `HAL Specification <http://stateless.co/hal_specification.html>`_
    """
    formats = ['hal', _CONTENT_TYPE]
    extra_headers = {'Content-Type': _CONTENT_TYPE}

    @property
    def formatted_body(self):
        """
        :return: The response body for the resource.
        :rtype: unicode
        """
        response = self._construct_resource(self.resource)
        return json.dumps(response)

    def _construct_resource(self, resource):
        """
        Constructs a full resource.  This can be used
        for either the primary resource or embedded resources

        :param ripozo.resources.resource_base.ResourceBase resource: The resource
            that will be constructed.
        :return: The resource represented according to the
            Hal specification
        :rtype: dict
        """
        resource_url = self.combine_base_url_with_resource_url(resource.url)
        parent_properties = resource.properties.copy()

        embedded, links = self.generate_relationship(resource.related_resources)
        embedded2, links2 = self.generate_relationship(resource.linked_resources)
        embedded.update(embedded2)
        links.update(links2)
        links.update(dict(self=dict(href=resource_url)))

        response = dict(_links=links, _embedded=embedded)
        response.update(parent_properties)
        return response

    def generate_relationship(self, relationship_list):
        """
        Generates an appropriately formatted embedded relationship
        in the HAL format.

        :param list[ripozo.viewsets.relationships.relationship.BaseRelationship] relationship_list: The
            relationship that an embedded version is being created for.
        :return: If it is a ListRelationship it will return a list/collection of the
            embedded resources.  Otherwise it returns a dictionary as specified
            by the HAL specification.
        :rtype: list|dict
        """
        # TODO clean this shit up.
        embedded_dict = {}
        links_dict = {}
        for relationship, field_name, embedded in relationship_list:
            rel = self._generate_relationship(relationship, embedded)
            if not rel:
                continue
            if embedded:
                embedded_dict[field_name] = rel
            else:
                links_dict[field_name] = rel
        return embedded_dict, links_dict

    def _generate_relationship(self, relationship, embedded):
        """
        Properly formats the relationship in a HAL ready format.

        :param ResourceBase|list[ResourceBase] relationship: The
            ResourceBase instance or list of resource bases.
        :param bool embedded: Whether or not the related resource
            should be embedded.
        :return: A list of dictionaries or dictionary representing
            the relationship(s)
        :rtype: list|dict
        """
        if isinstance(relationship, list):
            response = []
            for res in relationship:
                if not res.has_all_pks:
                    continue
                response.append(self._generate_relationship(res, embedded))
            return response
        if not relationship.has_all_pks:
            return
        if embedded:
            return self._construct_resource(relationship)
        else:
            return dict(href=relationship.url)

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
        body = json.dumps(dict(status=status_code, message=six.text_type(exc),
                               _embedded={}, _links={}))
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


