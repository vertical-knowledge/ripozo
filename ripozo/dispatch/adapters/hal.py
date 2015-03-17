from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.base import AdapterBase
from ripozo.viewsets.relationships.list_relationship import ListRelationship

import json
import six

_content_type = 'application/hal+json'


class HalAdapter(AdapterBase):
    """
    An adapter that formats the response in the HAL format
    A description of the HAL format can be found here:
    `HAL Specification <http://stateless.co/hal_specification.html>`_
    """
    formats = ['hal', _content_type]

    @property
    def extra_headers(self):
        """
        :return: Just returns a single header for the Content-Type
        :rtype: dict
        """
        return {'Content-Type': _content_type}

    @property
    def formatted_body(self):
        """
        :return: The response body for the resource.
        :rtype: unicode
        """
        links = self.generate_links_for_resource(self.resource)
        embedded = dict()
        parent_properties = self.resource.properties.copy()
        for field_name, relationship in six.iteritems(self.resource.relationships):
            embedded[field_name] = self.generate_embedded_relationship(relationship)
            parent_properties = relationship.remove_child_resource_properties(parent_properties)
        response = dict(_links=links, _embedded=embedded)
        response.update(parent_properties)
        return json.dumps(response)

    def generate_embedded_relationship(self, relationship):
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
        embedded = list()
        for related_resource in relationship.construct_resource(self.resource.properties):
            indv = dict(_links=self.generate_links_for_resource(related_resource))
            indv.update(related_resource.properties)
            embedded.append(indv)
        if not isinstance(relationship, ListRelationship):
            return embedded[0]
        return embedded


    def generate_links_for_resource(self, resource):
        """
        Currently only returns the "self" link.  Will work for
        embedded resources as well.

        :param ripozo.viewsets.resource_base.ResourceBase resource: The
            resource to generate the _links property for in the response
        :return: A dictionary of the named links
        :rtype: dict
        """
        resource_url = self.combine_base_url_with_resource_url(resource.url)
        return dict(self=dict(href=resource_url))
