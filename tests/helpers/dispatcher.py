from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.dispatch.dispatch_base import DispatcherBase


class FakeDispatcher(DispatcherBase):
    def __init__(self, *args, **kwargs):
        super(FakeDispatcher, self).__init__(*args, **kwargs)
        self.routes = {}

    def register_route(self, endpoint, **options):
        super(FakeDispatcher, self).register_route(endpoint, **options)
        current_route = self.routes.get(endpoint) or []
        current_route.append(options)
        self.routes[endpoint] = current_route

    @property
    def base_url(self):
        # Just to get coverage on empty abstract methods
        x = super(FakeDispatcher, self).base_url
        return 'http://127.0.0.1:7000/'