"""
Boring json which is just a basic
dump of the resource into json format.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.adapters import AdapterBase

import json

_CONTENT_TYPE = 'application/json'


class BoringJSONAdapter(AdapterBase):
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
        a json ready list of dictionaries.

        :param dict rel_dict:
        :param list relationships:
        :return: A list of the resources in dictionary format.
        :rtype: list
        """
        for resource, name, embedded in relationships:
            if name not in rel_dict:
                rel_dict[name] = []
            rel_dict[name].append(resource.properties)
