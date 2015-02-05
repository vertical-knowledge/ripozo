from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from flask import request, current_app
from rest.dispatch.dispatch_base import DispatcherBase
from werkzeug.routing import Rule
__author__ = 'Tim Martin'


class FlaskDispatcher(DispatcherBase):
    def register_route(self, endpoint, endpoint_func=None, route=None, methods=None, **options):
        current_app.url_map.add(Rule(route, ))