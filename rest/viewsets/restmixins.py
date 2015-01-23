from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Tim Martin'
import logging
from rest.decorators import apimethod
from rest.viewsets.base import APIBase

logger = logging.getLogger(__name__)

# TODO documentation


class Create(APIBase):
    @apimethod(methods=['POST'])
    def create(cls, values, *args, **kwargs):
        logger.info('Creating a model for resource {0}'.format(cls._resource_name))
        obj = cls._manager.create(values, *args, **kwargs)
        return cls(properties=obj, status_code=201)


class RetrieveList(APIBase):
    @apimethod(methods=['GET'])
    def retrieve_list(cls, filters, *args, **kwargs):
        logger.info('Retrieving a list of models for resource {0} '
                    'with filters {1}'.format(cls._resource_name, filters))
        results, next_query_args = cls._manager.retrieve_list(filters, *args, **kwargs)
        return cls(properties=results, meta=next_query_args, status_code=200)


class RetrieveSingle(APIBase):
    @apimethod(methods=['GET'])
    def retrieve(cls, primary_keys, *args, **kwargs):
        logger.info('Retrieving a model for resource {0}'
                    'with primary keys {0}'.format(cls._resource_name, primary_keys))
        obj = cls._manager.retrieve(primary_keys, *args, **kwargs)
        return cls(properties=obj, status_code=200)


class Update(APIBase):
    @apimethod(methods=['PUT', 'PATCH'])
    def update(cls, primary_keys, updates, *args, **kwargs):
        logger.info('Updating a model for resource {0}'
                    'with primary keys'.format(cls._resource_name, primary_keys))
        obj = cls._manager.update(primary_keys, updates, *args, **kwargs)
        return cls(properties=obj, status_code=200)


class Delete(APIBase):
    @apimethod(methods=['DELETE'])
    def remove(cls, primary_keys, *args, **kwargs):
        logger.info('Deleting a model for resource {0}'
                    'with primary keys'.format(cls._resource_name, primary_keys))
        cls._manager.delete(primary_keys, *args, **kwargs)
        return cls(status_code=204)
