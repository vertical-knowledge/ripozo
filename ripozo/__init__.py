import pkg_resources

__version__ = pkg_resources.get_distribution('ripozo').version


from ripozo.viewsets.resource_base import ResourceBase
from ripozo.decorators import apimethod