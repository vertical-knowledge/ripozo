from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.relationships.list_relationship import ListRelationship
from ripozo.viewsets.relationships.relationship import Relationship

import six


class LinksMixin(object):
    """
    A link is very similar to a relationship. Links are
    generally for meta information about the resource.
    Typically, this is going to be similar to be of the
    same resource as that returned.  For example, when
    paginating over a list, the reference to the next
    page in the list would be a link.

    By default, the links property on the ResourceBase
    (and any subclasses), will take any item in declared
    on the ``ResourceMeta.meta['links']`` attribute and
    pass it into the constructor for this class.

    This is a mixin and should be used in conjunction with
    a Relation class or subclass.
    """

    def construct_urls(self, properties):
        """
        A generator that returns the unicode urls
        for the resource. It appropriately places the
        primary keys from the relationship in the url path
        and takes the rest of the parameters and adds the
        rest of the properties as query parameters.  It
        uses the ``self._map_pks`` method to get the appropriate


        :param dict properties: The properties to construct the resource
            with.  These will first be passed to the Relationship.construct_resource
            method. Any properties that are not in the pks list on the resource
            will be added as query parameters.
        :return:
        :rtype:
        :raises: KeyError
        """
        for relationship in self.construct_resource(properties):
            path = relationship.url
            query_parts = []
            for name, value in six.iteritems(relationship.properties):
                if name not in relationship.pks:
                    query_parts.append('{0}&{1}'.format(name, value))
            query_string = '&'.join(query_parts)
            yield '{0}?{1}'.format(path, query_string)


class Link(Relationship, LinksMixin):
    """
    A builtin case for Links subclassed
    from the Relationship class
    """
    pass


class ListLink(ListRelationship, LinksMixin):
    """
    A builtin case for a list of links subclassed
     from the ListRelationship class
    """
    pass
