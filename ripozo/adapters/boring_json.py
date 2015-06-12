from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from ripozo.adapters import AdapterBase

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
    extra_headers = {'Content-Type': content_type}

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
        for resource, name, embedded in relationships:
            if name not in rel_dict:
                rel_dict[name] = []
            rel_dict[name].append(resource.properties)
