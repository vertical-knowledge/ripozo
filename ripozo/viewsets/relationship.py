from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from ripozo.viewsets.constructor import ResourceMetaClass
import six

__author__ = 'Tim Martin'


class Relationship(object):
    """
    Defines a relationship on a resource.  This allows
    you to create related resources and construct them
    appropriately.  As usual, the actual response is
    created by an adapter which must determine whether
    to return the whole resource, a link, etc...
    """

    def __init__(self, property_map=None, relation=None, embedded=False):
        """
        :param dict property_map: A map of the parent's property name
            to the corresponding related fields properties.  For example,
            it may be called "child" on the parent but it corresponds to
            the id field on the related field.
        :param unicode relation: The name of the resource class
            that this relation is a type of.  It uses a string so
            that you do not have to worry about the order of how relations
            were defined.  It looks up the actual type from the
            ResourceMetaClass.
        :param bool embedded: Indicates whether the related resource
            should be embedded in the parent resource when returned.
            Otherwise, a more basic representation will be used (e.g.
            a link or id)
        """
        self.property_map = property_map or {}
        self._relation = relation
        self.embedded = embedded

    @property
    def relation(self):
        """
        The ResourceBase subclass that describes the related object
        If no _relation property is available on the instance
        it returns None.

        :return: The ResourceBase subclass that describes the
            related resource
        :rtype: type
        """
        if self._relation:
            return ResourceMetaClass.registered_names_map[self._relation]
        return None

    def construct_resource(self, properties):
        """
        Takes the properties from the parent and
        and maps them to the named properties for the
        parent resource to its relationships

        :param dict properties:
        :return: An instance of a self.relation class that corresponds
            to this related resource
        :rtype: rest.viewsets.resource_base.ResourceBase
        """
        related_properties = self._map_pks(properties)
        return self.relation(properties=related_properties)

    def remove_child_resource_properties(self, properties):
        """
        Removes the properties that are supposed to be on the child
        resource and not on the parent resource.  It copies the properties
        argument before it removes the copied values.  It does not have
        side effects in other words.

        :param dict properties: The properties that are in the related
            resource map that should not be in the parent resource.
        :return: a dictionary of the updated properties
        :rtype: :py:class:`dict`
        """
        properties = properties.copy()
        for key in six.iterkeys(self.property_map):
            properties.pop(key)
        return properties

    def _map_pks(self, parent_properties):
        """
        Takes a dictionary of the values of the parent
        resources properties.  It then maps those properties
        to the named properties of the related resource
        and creates a dictionary of the related resources
        property values.

        :param dict parent_properties: A dictionary of the parent
            resource's properties.  The key is the name of the
            property and the value is the parent resources value
            for that property
        :return: A dictionary of the related resources properties.
            The key is the name of the related resource's property
            and the value is the value of that resource's property.
        :rtype: :py:class:`dict`
        """
        properties = {}
        for parent_prop, prop in six.iteritems(self.property_map):
            properties[prop] = parent_properties[parent_prop]
        return properties
