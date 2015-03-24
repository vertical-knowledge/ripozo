from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import json

import six

from ripozo.dispatch.adapters.base import AdapterBase
from ripozo.utilities import titlize_endpoint
from ripozo.viewsets.resource_base import create_url
from ripozo.viewsets.constants import status, input_categories


_content_type = 'application/vnd.siren+json'


class SirenAdapter(AdapterBase):
    """
    An adapter that formats the response in the SIREN format.
    A description of a SIREN format can be found here:
    `SIREN specification <https://github.com/kevinswiber/siren>`_
    """
    formats = ['siren', _content_type]

    @property
    def formatted_body(self):
        """
        Gets the formatted body of the response in unicode form.

        :return: The siren formatted response body
        :rtype: unicode
        """
        if self.resource.status == status.DELETED:
            return ''  # TODO write test to prevent regressions here

        links = [dict(rel=['self'], href=self.combine_base_url_with_resource_url(self.resource.url))]

        entities, updated_properties = self.get_entities_and_remove_related_properties()
        response = dict(properties=updated_properties, actions=self._actions,
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
            all_methods = options.get('methods', [])
            if len(all_methods) == 0:
                meth = 'GET'
            else:
                meth = all_methods[0]
            base_route = options.get('route', self.resource.base_url)
            route = create_url(base_route, **self.resource.properties)
            route = self.combine_base_url_with_resource_url(route)
            fields = self.generate_fields_for_endpoint_funct(options.get('endpoint_func'))
            actn = dict(name=endpoint, title=titlize_endpoint(endpoint), method=meth, href=route, fields=fields)
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
        fields = []
        fields_method = getattr(endpoint_func, 'fields', None)
        if not fields_method:
            return []

        for field in fields_method(self.resource.manager):
            if field.arg_type is input_categories.URL_PARAMS:
                continue
            fields.append(dict(name=field.name, type=field.field_type.__name__,
                               location=field.arg_type, required=field.required))
        return fields

    def get_entities_and_remove_related_properties(self):
        """
        Gets a list of related entities in an appropriate SIREN format

        :return: A list of entities
        :rtype: list
        """
        entities = []
        parent_properties = self.resource.properties.copy()
        for field_name, relationship in six.iteritems(self.resource.relationships):
            for related_resource in relationship.construct_resource(self.resource.properties):
                ent = {'class': [relationship.relation.resource_name], 'rel': [field_name]}
                resource_url = self.combine_base_url_with_resource_url(related_resource.url)
                if not relationship.embedded:
                    ent['href'] = resource_url
                else:
                    ent['properties'] = related_resource.properties
                    ent['links'] = [dict(rel=['self'], href=resource_url)]
                entities.append(ent)
            parent_properties = relationship.remove_child_resource_properties(parent_properties)
        return entities, parent_properties


    @property
    def extra_headers(self):
        """
        The headers that should be appended to the response

        :return: a dictionary of the headers to be set on the
            response
        :rtype: dict
        """
        return {'Content-Type': _content_type}
