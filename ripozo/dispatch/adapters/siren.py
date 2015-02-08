from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from ripozo.dispatch.adapters.base import AdapterBase
from ripozo.utilities import titlize_endpoint
from ripozo.viewsets.resource_base import create_url
import json
import six

_content_type = 'application/vnd.siren+json'


class SirenAdapter(AdapterBase):
    """
    An adapter that formats the response in the SIREN format.
    A description of a SIREN format can be found here:
    `SIREN specification <https://github.com/kevinswiber/siren>`_
    """
    formats = ['siren', _content_type]

    @property
    def formatted_body(self):
        """
        Gets the formatted body of the response in unicode form.

        :return: The siren formatted response body
        :rtype: unicode
        """
        actions = []
        for endpoint, options in six.iteritems(self.resource.endpoint_dictionary):
            options = options[0]
            all_methods = options.get('methods', [])
            if len(all_methods) == 0:
                meth = 'GET'
            else:
                meth = all_methods[0]
            base_route = options.get('route', self.resource.base_url)
            route = create_url(base_route, **self.resource.properties)
            actn = dict(name=endpoint, title=titlize_endpoint(endpoint), method=meth, href=route)
            actions.append(actn)
        links = [dict(rel=['self'], href=self.resource.url)]

        response = dict(properties=self.resource.properties, actions=actions,
                        links=links)
        response['class'] = [self.resource.resource_name]
        return json.dumps(response)

    @property
    def extra_headers(self):
        """
        The headers that should be appended to the response

        :return: a list of the headers to be set on the
            response
        :rtype: list
        """
        return [{'Content-Type': _content_type}]
