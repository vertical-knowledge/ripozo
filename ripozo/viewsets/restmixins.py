from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.viewsets.relationships.relationship import Relationship
from ripozo.viewsets.relationships.list_relationship import ListRelationship
from ripozo.decorators import apimethod, translate, classproperty
from ripozo.viewsets.resource_base import ResourceBase

import logging
import six

logger = logging.getLogger(__name__)

# TODO need to test and doc all of this


class Create(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['POST'], no_pks=True)
    @translate(manager_field_validators=True, validate=True)
    def create(cls, request, *args, **kwargs):
        logger.debug('Creating a resource using manager {0}'.format(cls._manager))
        props = cls.manager.create(request.body_args)
        meta = dict(links=dict(created=props))
        return cls(properties=props, meta=meta, status_code=201)

    @classproperty
    def links(cls):
        """
        Appends the "created" link to the _links
        and returns the corresponding tuple.

        :return: The links defined on the class plus
            the "created" link that references the newly
            created link.
        :rtype: tuple
        """
        links = cls._links or tuple()
        return links + (Relationship('created', relation=cls.__name__, embedded=True), )


class Retrieve(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    @translate(manager_field_validators=True)
    def retrieve(cls, request, *args, **kwargs):
        logger.debug('Retrieving a resource using the manager {0}'.format(cls._manager))
        props = cls.manager.retrieve(request.url_params)
        return cls(properties=props, status_code=200)


class RetrieveList(Retrieve):
    __abstract__ = True
    _indv_name = None

    @classproperty
    def indv_name(cls):
        return cls._indv_name or cls.resource_name

    @apimethod(methods=['GET'], no_pks=True)
    @translate(manager_field_validators=True, validate=False)
    def retrieve_list(cls, request, *args, **kwargs):
        logger.debug('Retrieving list of resources using manager {0}'.format(cls._manager))
        props, meta = cls.manager.retrieve_list(request.query_args)
        return cls(properties={cls.resource_name: props}, meta=meta, status_code=200)

    @classproperty
    def links(cls):
        """
        Appends the "next" and "previous" links to the
        _links and returns the corresponding tuple.

        :return: The links defined on the class plus
            the "next" and "previous" link that references
            the newly created link.
        :rtype: tuple
        """
        links = cls._links or tuple()
        return links + (Relationship('next', relation=cls.__name__),
                        Relationship('previous', relation=cls.__name__),)

    @classproperty
    def relationships(cls):
        """
        Appends the ListRelationship relationship that corresponds
        to the items returned.

        :return: The relationships on the class plus the
            cls.__name__
        :rtype:
        """
        relationships = cls._relationships or tuple()
        return relationships + (ListRelationship(cls.indv_name, relation=cls.__name__),)


class Update(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['PATCH'])
    @translate(manager_field_validators=True, skip_required=True, validate=True)
    def update(cls, request, *args, **kwargs):
        logger.debug('Updating a resource using the manager {0}'.format(cls._manager))
        props = cls.manager.update(request.url_params, request.body_args)
        return cls(properties=props, status_code=200)


class Delete(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['DELETE'])
    @translate(manager_field_validators=True)
    def delete(cls, request, *args, **kwargs):
        logger.debug('Deleting the resource using manager {0}'.format(cls._manager))
        props = cls.manager.delete(request.url_params)
        return cls(properties=props)


class RetrieveUpdate(Retrieve, Update):
    __abstract__ = True


class RetrieveUpdateDelete(Retrieve, Update, Delete):
    __abstract__ = True


class CreateRetrieve(Create, Retrieve):
    __abstract__ = True


class CreateRetrieveUpdate(Create, Retrieve, Update):
    __abstract__ = True


class CreateRetrieveUpdateDelete(Create, Retrieve, Update, Delete):
    __abstract__ = True


class CreateRetrieveListUpdateDelete(Create, RetrieveList, Update, Delete):
    __abstract__ = True
