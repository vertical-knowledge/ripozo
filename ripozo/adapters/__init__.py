"""
Contains the builtin adapters as well
as the AdapterBase abstract base class.
Inherit from that to ensure a proper implementation
of the adapter.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .base import AdapterBase
from .siren import SirenAdapter
from .hal import HalAdapter
from .basic_json import BasicJSONAdapter
from .jsonapi import JSONAPIAdapter
