__author__ = 'Tim Martin'
import logging
from flask import request, jsonify, Response
from webargs.flaskparser import FlaskParser
from cassandra_rest.decorators import apimethod
from cassandra_rest.viewsets.base import APIBase


parser = FlaskParser()


class Create(APIBase):
    @apimethod(pluralized=True, methods=['POST'])
    def create(self):
        manager = self._get_manager()
        kwargs = parser.parse(manager.arg_parser, request, targets=('form', 'json', 'url_params'))
        obj = manager.create(kwargs)
        obj_name = self.resource_name if self.resource_name is not None else self.model_name
        response = jsonify({obj_name: obj})
        response.status_code = 201
        return response


class RetrieveList(APIBase):
    @apimethod(pluralized=True, methods=['GET'])
    def retrieve_list(self):
        manager = self._get_manager()
        filters = parser.parse(manager.arg_parser, request, targets=('url_params', 'querystring'))
        results, next_query_args = manager.retrieve_list(filters)
        if next_query_args.get('next') is None:
            next_page_url = None
        else:
            next_page_url = '{0}?{1}'.format(self.get_base_url(pluralized=True), next_query_args['next'])
        next_query_args['next'] = next_page_url
        response = jsonify({self._pluralization: results, 'meta': next_query_args})
        response.status_code = 200
        return response


class RetrieveSingle(APIBase):
    @apimethod(pluralized=False, methods=['GET'])
    def retrieve(self, **primary_keys):
        manager = self._get_manager()
        obj = manager.retrieve(primary_keys)
        obj_name = self.resource_name if self.resource_name is not None else self.model_name
        response = jsonify({obj_name: obj})
        response.status_code = 200
        return response


class Update(APIBase):
    @apimethod(pluralized=False, methods=['PUT', 'PATCH'])
    def update(self, **primary_keys):
        manager = self._get_manager()
        kwargs = parser.parse(manager.arg_parser, request, targets=('form', 'json', 'url_params'))
        obj = manager.update(primary_keys, kwargs)
        obj_name = self.resource_name if self.resource_name is not None else self.model_name
        response = jsonify({obj_name: obj})
        response.status_code = 200
        return response


class Delete(APIBase):
    @apimethod(pluralized=False, methods=['DELETE'])
    def remove(self, **primary_keys):
        manager = self._get_manager()
        manager.delete(primary_keys)
        response = Response()
        response.status_code = 204
        return response


@parser.target_handler('url_params')
def parse_url_kwargs(request, name, arg):
    """
    This allows webargs to find the keyword args contained in the url
    (e.g. It would grab the kwarg model_id from the url route /somemodel/<model_id>)
    """
    kwargs = request.view_args.get(name)
    logger = logging.getLogger(__name__)
    logger.debug('Parsed kwargs from url')
    return kwargs