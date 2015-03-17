from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.adapters.base import AdapterBase
from ripozo.viewsets.relationships.list_relationship import ListRelationship

import json
import six

content_type = 'application/json'


class BoringJSONAdapter(AdapterBase):
    """
    Just a plain old JSON dump of the properties.
    Nothing exciting.

    Format:

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
    formats = ['json', content_type]

    @property
    def extra_headers(self):
        # TODO docs
        return {'Content-Type': content_type}

    @property
    def formatted_body(self):
        response = dict()
        parent_properties = self.resource.properties.copy()
        for field_name, relationship in six.iteritems(self.resource.relationships):
            response[field_name] = self.generate_relationship(relationship)
            parent_properties = relationship.remove_child_resource_properties(parent_properties)
        response.update(parent_properties)
        return json.dumps({self.resource.resource_name: response})

    def generate_relationship(self, relationship):
        embedded = list()
        for related_resource in relationship.construct_resource(self.resource.properties):
            embedded.append(related_resource.properties)
        if not isinstance(relationship, ListRelationship):
            return embedded[0]
        return embedded