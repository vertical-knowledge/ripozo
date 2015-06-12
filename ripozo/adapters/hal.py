from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from ripozo.adapters import AdapterBase

_content_type = 'application/hal+json'


class HalAdapter(AdapterBase):
    """
    An adapter that formats the response in the HAL format.
    A description of the HAL format can be found here:
    `HAL Specification <http://stateless.co/hal_specification.html>`_
    """
    formats = ['hal', _content_type]
    extra_headers = {'Content-Type': _content_type}

    @property
    def formatted_body(self):
        """
        :return: The response body for the resource.
        :rtype: unicode
        """
        resource_url = self.combine_base_url_with_resource_url(self.resource.url)
        parent_properties = self.resource.properties.copy()

        embedded, links = self.generate_relationship(self.resource.related_resources)
        embedded2, links2 = self.generate_relationship(self.resource.linked_resources)
        embedded.update(embedded2)
        links.update(links2)
        links.update(dict(self=dict(href=resource_url)))

        response = dict(_links=links, _embedded=embedded)
        response.update(parent_properties)
        return json.dumps(response)

    def generate_relationship(self, relationship_list):
        """
        Generates an appropriately formated embedded relationship
        in the HAL format.

        :param ripozo.viewsets.relationships.relationship.BaseRelationship relationship: The
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
            return relationship.properties
        else:
            return dict(href=relationship.url)
