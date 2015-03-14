from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import apimethod
from ripozo.viewsets.resource_base import ResourceBase

import logging

logger = logging.getLogger(__name__)


class Create(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['POST'])
    def create(cls, request, *args, **kwargs):
        logger.debug('Creating a resource using manager {0}'.format(cls._manager))
        request.validate(cls.manager.field_validators)
        props = cls.manager.create(request.body_args)
        return cls(properties=props)


class RetrieveList(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    def retrieve_list(cls, request, *args, **kwargs):
        logger.debug('Retrieving list of resources using manager {0}'.format(cls._manager))
        request.translate(cls.manager.field_validators)
        props, meta = cls.manager.retrieve_list(request.query_args)
        props.update(meta)
        return cls(properties=props)


class Retrieve(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    def retrieve(cls, request, *args, **kwargs):
        logger.debug('Retrieving a resource using the manager {0}'.format(cls._manager))
        request.translate(cls.manager.field_validators)
        props = cls.manager.retrieve(request.url_params)
        return cls(properties=props)


class Update(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['PATCH'])
    def update(cls, request, *args, **kwargs):
        logger.debug('Updating a resource using the manager {0}'.format(cls._manager))
        request.validate(cls.manager.field_validators, skip_required=True)
        props = cls.manager.update(request.url_params, request.body_args)
        return cls(properties=props)


class Delete(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['DELETE'])
    def delete(cls, request, *args, **kwargs):
        logger.debug('Deleting the resource using manager {0}'.format(cls._manager))
        request.translate(cls.manager.field_validators)
        props = cls.manager.delete(request.url_params)
        return cls(properties=props)


class RetrieveUpdate(Retrieve, Update):
    __abstract__ = True


class RetrieveUpdateDelete(Retrieve, Update, Delete):
    __abstract__ = True


class CreateRetrieveList(Create, RetrieveList):
    __abstract__ = True
