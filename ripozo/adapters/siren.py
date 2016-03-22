"""
Siren protocol adapter.  See `SIREN specification <https://github.com/kevinswiber/siren>`_.
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
from ripozo.resources.constants import input_categories
from ripozo.resources.resource_base import create_url
from ripozo.utilities import titlize_endpoint
from ripozo.wsgi.parse import construct_request_from_wsgi_environ, json_loads_backwards_compatible

_CONTENT_TYPE = 'application/vnd.siren+json'
_json_loads_backwards_compatible = partial(json_loads_backwards_compatible, content_type=_CONTENT_TYPE)


class SirenAdapter(AdapterBase):
    """
    An adapter that formats the response in the SIREN format.
    A description of a SIREN format can be found here:
    `SIREN specification <https://github.com/kevinswiber/siren>`_
    """
    formats = [_CONTENT_TYPE, 'siren']
    extra_headers = {'Content-Type': _CONTENT_TYPE}

    @property
    def formatted_body(self):
        """
        Gets the formatted body of the response in unicode form.
        If ``self.status_code == 204`` then this will
        return an empty string.

        :return: The siren formatted response body
        :rtype: unicode
        """
        # 204's are supposed to be empty responses
        if self.status_code == 204:
            return ''

        links = self.generate_links()

        entities = self.get_entities()
        response = dict(properties=self.resource.properties, actions=self._actions,
                        links=links, entities=entities)

        # need to do this separately since class is a reserved keyword
        response['class'] = [self.resource.resource_name]
        return json.dumps(response)

    @property
    def _actions(self):
        """
        Gets the list of actions in an appropriately SIREN format

        :return: The list of actions
        :rtype: list
        """
        actions = []
        for endpoint, options in six.iteritems(self.resource.endpoint_dictionary()):
            options = options[0]
            all_methods = options.get('methods', ('GET',))
            meth = all_methods[0] if all_methods else 'GET'
            base_route = options.get('route', self.resource.base_url)
            route = create_url(base_route, **self.resource.properties)
            route = self.combine_base_url_with_resource_url(route)
            fields = self.generate_fields_for_endpoint_funct(options.get('endpoint_func'))
            actn = dict(name=endpoint, title=titlize_endpoint(endpoint),
                        method=meth, href=route, fields=fields)
            actions.append(actn)
        return actions

    def generate_fields_for_endpoint_funct(self, endpoint_func):
        """
        Returns the action's fields attribute in a SIREN
        appropriate format.

        :param apimethod endpoint_func:
        :return: A dictionary of action fields
        :rtype: dict
        """
        return_fields = []
        fields_method = getattr(endpoint_func, 'fields', None)
        if not fields_method:
            return []
        fields = fields_method(self.resource.manager)

        for field in fields:
            if field.arg_type is input_categories.URL_PARAMS:
                continue
            field_dict = dict(name=field.name, type=field.field_type.__name__,
                              location=field.arg_type, required=field.required)
            return_fields.append(field_dict)
        return return_fields

    def generate_links(self):
        """
        Generates the Siren links for the resource.

        :return: The list of Siren formatted links.
        :rtype: list
        """
        href = self.combine_base_url_with_resource_url(self.resource.url)
        links = [dict(rel=['self'], href=href)]
        for link, link_name, embedded in self.resource.linked_resources:
            links.append(dict(rel=[link_name],
                              href=self.combine_base_url_with_resource_url(link.url)))
        return links

    def get_entities(self):
        """
        Gets a list of related entities in an appropriate SIREN format

        :return: A list of entities
        :rtype: list
        """
        entities = []
        for resource, name, embedded in self.resource.related_resources:
            for ent in self.generate_entity(resource, name, embedded):
                entities.append(ent)
        return entities

    def generate_entity(self, resource, name, embedded):
        """
        A generator that yields entities
        """
        if isinstance(resource, list):
            for res in resource:
                for ent in self.generate_entity(res, name, embedded):
                    yield ent
        else:
            if not resource.has_all_pks:
                return
            ent = {'class': [resource.resource_name], 'rel': [name]}
            resource_url = self.combine_base_url_with_resource_url(resource.url)
            if not embedded:
                ent['href'] = resource_url
            else:
                ent['properties'] = resource.properties
                ent['links'] = [dict(rel=['self'], href=resource_url)]
            yield ent

    @classmethod
    def format_exception(cls, exc):
        """
        Takes an exception and appropriately formats it
        in the siren format.  Mostly.  It doesn't return
        a self in this circumstance.

        :param Exception exc: The exception to format.
        :return: A tuple containing: response body, format,
            http response code
        :rtype: tuple
        """
        status_code = getattr(exc, 'status_code', 500)
        body = {'class': ['exception', exc.__class__.__name__],
                'actions': [], 'entities': [], 'links': [],
                'properties': dict(status=status_code, message=six.text_type(exc))}
        return json.dumps(body), cls.formats[0], status_code

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
