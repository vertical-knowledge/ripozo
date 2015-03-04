from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.relationships.relationship import Relationship


class ListRelationship(Relationship):
    """
    Special case for a list of relationships.
    """

    def __init__(self, list_name, relation=None, embedded=False):
        """
        A special case for list relationships.

        :param unicode list_name: The name of the list on the resource.
        :param unicode relation: The ResourceBase subclass that describes the individual
            items in the list
        :param bool embedded: An indicator to the adapter for whether the resource should be
            embedded or not
        """
        super(ListRelationship, self).__init__(relation=relation, embedded=embedded)
        self.list_name = list_name

    def construct_resource(self, properties):
        # TODO
        objects = properties.get(self.list_name, [])
        for obj in objects:
            yield self.relation(properties=obj)

    def remove_child_resource_properties(self, properties):
        # TODO
        properties = properties.copy()
        properties.pop(self.list_name)
        return properties