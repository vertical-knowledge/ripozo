from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from flask import request, jsonify
from rest.dispatch.dispatch_base import DispatcherBase
from werkzeug.routing import Rule, Map
import json
__author__ = 'Tim Martin'


# TODO docs
class FlaskDispatcher(DispatcherBase):
    def __init__(self, app):
        self.app = app
        self.url_map = Map()
        self.function_for_endpoint = {}

    def register_route(self, endpoint, endpoint_func=None, route=None, methods=None, **options):
        self.app.add_url_rule(route, None, self.flask_dispatch, methods=methods, **options)
        self.url_map.add(Rule(route, endpoint=endpoint, methods=methods))
        self.function_for_endpoint[endpoint] = endpoint_func

    def flask_dispatch(self, **urlparams):
        urls = self.url_map.bind_to_environ(request.environ)
        request_args = request.args.copy()
        format_type = request_args.pop('format', 'siren')
        endpoint, args = urls.match()
        endpoint_func = self.function_for_endpoint[endpoint]
        adapter = self.dispatch(endpoint_func, format_type, urlparams, request_args, request.data)
        response = adapter.get_formatted_body()
        response = json.loads(response)
        return jsonify(response)
