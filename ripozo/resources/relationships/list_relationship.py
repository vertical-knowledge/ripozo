"""
Contains the list relationship class.
Extends the relationship class slightly.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.resources.relationships.relationship import Relationship
from ripozo.utilities import get_or_pop


class ListRelationship(Relationship):
    """
    Special case for a list of relationships.
    """

    def construct_resource(self, properties):
        """
        Takes a list of properties and returns a generator that
        yields Resource instances.  These related ResourceBase subclass
        will be asked to construct an instance with the keyword argument
        properties equal to each item in the list of properties provided to
        this function.

        :param dict properties: A dictionary of the properties
            on the parent model.  The list_name provided in the construction
            of an instance of this class is used to find the list that will be
            iterated over to generate the resources.
        :return: A generator that yields the relationships.
        :rtype: types.GeneratorType
        """
        objects = get_or_pop(properties, self.name, [], pop=self.remove_properties)
        resources = []
        for obj in objects:
            res = self.relation(properties=obj, query_args=self.query_args,
                                include_relationships=self.embedded)
            resources.append(res)
        return resources
