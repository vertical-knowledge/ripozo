"""
Contains the adapter for the
`JSON API <http://jsonapi.org/format/>`_.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import six

from ripozo import ResourceBase
from ripozo.adapters.base import AdapterBase
from ripozo.exceptions import JSONAPIFormatException
from ripozo.resources.constructor import ResourceMetaClass
from ripozo.utilities import join_url_parts

_CONTENT_TYPE = 'application/vnd.api+json'


class JSONAPIAdapter(AdapterBase):
    """
    An adapter for formatting and ResourceBase
    instance in an appropriate format.  See the
    `specification <http://jsonapi.org/format/>`_
    for more details on what format it will return.
    """
    formats = [_CONTENT_TYPE]
    extra_headers = {'Content-Type': _CONTENT_TYPE}

    @property
    def formatted_body(self):
        """
        Returns a string in the
        `JSON API format. <http://jsonapi.org/format/>`_

        :return: The appropriately formatted string
        :rtype: unicode|str
        """
        data = self._construct_data(self.resource, embedded=True)
        return json.dumps(dict(data=data))

    def _construct_data(self, resource, embedded=True):
        """
        Constructs a resource object according to this
        `part of the specification <http://jsonapi.org/format/#document-resource-objects>`_

        :param ResourceBase resource: The resource to format
        :param bool embedded: A flag to indicate whether
            all of the data should be included.
        :return: A dictionary representing the resource
            according to the specification
        :rtype: dict
        """
        id_ = self._construct_id(resource)
        data = dict(id=id_, type=resource.resource_name)
        if embedded:
            data['relationships'] = self._construct_relationships(resource)
            data['links'] = self._construct_links(resource)
            data['attributes'] = resource.properties
        else:
            data['links'] = {'self': self.combine_base_url_with_resource_url(resource.url)}
        return data

    def _construct_links(self, resource):
        """
        Constructs the links object according
        to `this section <http://jsonapi.org/format/#document-links>`_

        :param ResourceBase resource: The links from this resource
            instance will be used to construct the links object.
        :return: A dictionary representing the links object
        :rtype: dict
        """
        self_url = self.combine_base_url_with_resource_url(resource.url)
        links = {'self': self_url}
        for link, name, embedded in resource.linked_resources:
            links[name] = self.combine_base_url_with_resource_url(link.url)
        return links

    @staticmethod
    def _construct_id(resource):
        """
        Constructs a JSON API compatible id.
        May not work particularly well for composite ids since
        apparently JSON API hates them.  It will simply
        join the pks with a `"/"` in the appropriate order.
        Additionally, for resources with no_pks=True, it
        will return an empty string.

        :param ResourceBase resource: The resource whose
            id needs to be constructed.
        :return: The id in a format `<pk1>/<pk2>`
        :rtype: unicode
        """
        if resource.no_pks:
            return ""
        pks = resource.pks
        id_parts = [resource.item_pks[pk] for pk in pks]
        id_ = join_url_parts(*id_parts)
        return id_

    def _construct_relationships(self, resource):
        """
        Constructs the relationships according to the
        `specification <http://jsonapi.org/format/#document-resource-object-relationships>`_

        :param ResourceBase resource: This is the resource
            that the relationships will be constructed for.
            It will user the `related_resources` attribute
            on the resource to construct the resources
        :return: The dictionary representing the relationships
            in the appropriate format.
        :rtype: dict
        """
        # TODO docs
        relationships = dict()
        for resource, name, embedded in resource.related_resources:
            if name not in relationships:
                relationships[name] = dict(data=[])
            data = relationships[name]['data']
            if isinstance(resource, ResourceBase):
                data.append(self._construct_data(resource, embedded=embedded))
            else:
                for res in resource:
                    data.append(self._construct_data(res, embedded=embedded))
        return relationships

    @classmethod
    def format_exception(cls, exc):
        """
        Responsible for formatting the exception according to the
        `error formatting specification <http://jsonapi.org/format/#errors>`_

        :param Exception exc: The exception to format
        :return: The response body, content type and status code
            as a tuple in that order.
        :rtype: unicode, unicode, int
        """
        status_code = getattr(exc, 'status_code', 500)
        error = dict(
            status=status_code,
            title=exc.__class__.__name__,
            detail=six.text_type(exc)
        )
        body = json.dumps(dict(errors=[error]))
        return body, _CONTENT_TYPE, status_code

    @classmethod
    def format_request(cls, request):
        """
        Unwraps a JSONAPI request according
        to the `specification .<http://jsonapi.org/format/#crud>`_
        Basically, it reformats the attributes and relationships to
        be top level and dot formatted instead of an underlying dictionary.

        :param RequestContainer request: The request whose request
            body should be updated
        :return: The updated request ready for ripozo.
        :rtype: RequestContainer
        """
        if request.body_args:
            try:
                data = request.body_args['data']
            except KeyError:
                raise JSONAPIFormatException('Any request with a request body'
                                             'must include a "data" attribute.')
            try:
                body = data['attributes']
            except KeyError:
                raise JSONAPIFormatException('Any request with a request body'
                                             'must include a "data" attribute '
                                             'with an "attributes" attribute within it')
            for name, value in six.iteritems(data.get('relationships', {})):
                if 'data' not in value or 'id' not in value['data'] or 'type' not in value['data']:
                    raise JSONAPIFormatException('All relationships must include a "data" '
                                                 'attribute with "id" and "type" attributes.')
                ids_dict = cls._parse_id(value['data']['id'], value['data']['type'])
                attributes = dict()
                for key, val in six.iteritems(ids_dict):
                    attributes['{0}.{1}'.format(name, key)] = val
                body.update(attributes)
            request.body_args = body
        return request

    @staticmethod
    def _parse_id(id_, resource_name):
        if resource_name not in ResourceMetaClass.registered_resource_names_map:
            raise JSONAPIFormatException('The resource "{0}" is not a valid type'.format(resource_name))
        resource_class = ResourceMetaClass.registered_resource_names_map[resource_name]
        ids = id_.split('/')
        if len(ids) != len(resource_class.pks):
            raise JSONAPIFormatException("Unsatisfactory id.  There are an unequal number"
                                         "of pks among the ids {0}".format(ids))
        return dict(zip(resource_class.pks, ids))
