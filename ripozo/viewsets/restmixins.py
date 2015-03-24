from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import apimethod, translate
from ripozo.viewsets.resource_base import ResourceBase

import logging

logger = logging.getLogger(__name__)

# TODO need to test and doc all of this


class Create(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['POST'])
    @translate(manager_field_validators=True, validate=True)
    def create(cls, request, *args, **kwargs):
        logger.debug('Creating a resource using manager {0}'.format(cls._manager))
        props = cls.manager.create(request.body_args)
        return cls(properties=props)


class RetrieveList(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    def retrieve_list(cls, request, *args, **kwargs):
        logger.debug('Retrieving list of resources using manager {0}'.format(cls._manager))
        props, meta = cls.manager.retrieve_list({})
        return cls(properties={cls.resource_name: props}, meta=meta)


class Retrieve(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    @translate(manager_field_validators=True)
    def retrieve(cls, request, *args, **kwargs):
        logger.debug('Retrieving a resource using the manager {0}'.format(cls._manager))
        props = cls.manager.retrieve(request.url_params)
        return cls(properties=props)


class Update(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['PATCH'])
    @translate(manager_field_validators=True, skip_required=True, validate=True)
    def update(cls, request, *args, **kwargs):
        logger.debug('Updating a resource using the manager {0}'.format(cls._manager))
        props = cls.manager.update(request.url_params, request.body_args)
        return cls(properties=props)


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


class CreateRetrieveList(RetrieveList, Create):
    __abstract__ = True
