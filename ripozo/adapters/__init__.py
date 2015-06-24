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

from ripozo.adapters.base import AdapterBase
from ripozo.adapters.siren import SirenAdapter
from ripozo.adapters.hal import HalAdapter
from ripozo.adapters.boring_json import BoringJSONAdapter
