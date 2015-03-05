from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Tim Martin'
import logging
from ripozo.decorators import apimethod
from ripozo.viewsets.resource_base import ResourceBase

logger = logging.getLogger(__name__)

# TODO documentation


class Create(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['POST'])
    def create(cls, request,  *args, **kwargs):
        logger.info('Creating a model for resource {0}'.format(cls.resource_name))
        request.validate(fields=cls.manager.field_validators)
        obj = cls.manager.create(request.body_args, *args, **kwargs)
        return cls(properties=obj)


class RetrieveList(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    def retrieve_list(cls, request, *args, **kwargs):
        request.translate(fields=cls.manager.field_validators)
        results, next_query_args = cls.manager.retrieve_list(request.query_args, *args, **kwargs)
        results = dict(objects=results)
        results.update(next_query_args)
        return cls(properties=results)


class RetrieveSingle(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['GET'])
    def retrieve(cls, request, *args, **kwargs):
        request.translate(cls.manager.field_validators)
        obj = cls.manager.retrieve(request.url_params, *args, **kwargs)
        return cls(properties=obj)


class Update(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['PATCH'])
    def update(cls, request, *args, **kwargs):
        request.translate(cls.manager.field_validators)
        obj = cls.manager.update(request.url_params, request.body_args, *args, **kwargs)
        return cls(properties=obj)


class Delete(ResourceBase):
    __abstract__ = True

    @apimethod(methods=['DELETE'])
    def remove(cls, request, *args, **kwargs):
        request.translate(fields=cls.manager.field_validators)
        cls.manager.delete(request.url_params, *args, **kwargs)
        return cls()
