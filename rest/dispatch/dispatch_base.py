from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod
from rest.dispatch.adapters.contructor import AdapterMeta
from rest.dispatch.adapters.siren import SirenAdapter
from rest.viewsets.constructor import ResourceMetaClass
import six

__author__ = 'Tim Martin'


@six.add_metaclass(ABCMeta)
class DispatcherBase(object):
    # TODO docs
    def setup_all_class_routes(self, klass):
        for endpoint, routes in klass.endpoint_dictionary.iteritems():
            for options in routes:
                options = options.copy()
                route = options.pop('route', klass.base_url)
                methods = options.pop('methods', ['GET'])
                self.register_route(endpoint, route=route, methods=methods, **options)

    @abstractmethod
    def register_route(self, endpoint, endpoint_func=None, route=None, methods=None, **options):
        pass

    def dispatch(self, endpoint_func, format_type, *args, **kwargs):
        result = endpoint_func(*args, **kwargs)
        adapter_class = AdapterMeta.formats.get(format_type)
        adapter = adapter_class(result)
        return adapter