from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.resources.relationships.relationship import Relationship


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
        objects = properties.pop(self.name, [])
        objects = objects or []
        resources = []
        for obj in objects:
            res = self.relation(properties=obj, query_args=self.query_args,
                                include_relationships=self.embedded)
            resources.append(res)
        return resources

    def remove_child_resource_properties(self, properties):
        """
        Removes the item from the properties dict with the key
        that matches this instance's list_name attribute.  It
        copies the properties and pops the property from the copy
        before returning it.

        :param dict properties: The properties with the list_name
            key and value to be removed.
        :return: The updated properties dict.  This is actually a copy
            of the original to prevent side effects.
        :rtype: dict
        """
        properties = properties.copy()
        properties.pop(self.name, None)
        return properties
