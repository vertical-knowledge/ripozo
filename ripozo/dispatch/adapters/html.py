from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from jinja2 import Environment, PackageLoader

from ripozo.dispatch.adapters.base import AdapterBase
from ripozo.dispatch.adapters.siren import SirenAdapter

import json
import os

base_dir = os.path.dirname(__file__)
html_template = 'html_adapter_formats/templates'

env = Environment(loader=PackageLoader('ripozo', html_template))
template = env.get_template('html_adapter_template.html')

content_type = 'text/html'


class HtmlAdapter(AdapterBase):
    # TODO docs
    formats = ['html', content_type]

    @property
    def formatted_body(self):
        siren = SirenAdapter(self.resource, base_url=self.base_url)
        data = json.loads(siren.formatted_body)
        response = template.render(**data)
        return response

    @property
    def extra_headers(self):
        return {'Content-Type': content_type}
