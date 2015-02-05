from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from rest.dispatch.adapters.base import AdapterBase
from rest.viewsets.resource_base import create_url
import json
import re
import six
__author__ = 'Tim Martin'
_content_type = 'application/vnd.siren+json'


class SirenAdapter(AdapterBase):
    formats = ['siren', _content_type]

    # TODO docs
    def get_formatted_body(self):
        actions = []
        for endpoint, options in self.resource.endpoint_dictionary.iteritems():
            all_methods = options.get('methods', [])
            if len(all_methods) == 0:
                meth = 'GET'
            else:
                meth = all_methods[0]
            base_route = options.get('route', self.resource.base_url)
            route = create_url(base_route, **self.resource.properties)
            actn = dict(name=endpoint, title=endpoint, method=meth, href=route)
            actions.append(actn)
        links = [dict(rel=['self'], href=self.resource.url)]

        response = dict(properties=self.resource.properties, actions=actions,
                        links=links)
        response['class'] = [self.resource._resource_name]
        return json.dumps(response)

    def extra_headers(self):
        return [{'Content-Type': _content_type}]


def titlize_endpoint(endpoint):
    # TODO actually capitalize it appropriately
    return endpoint
