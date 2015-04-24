import pkg_resources

__version__ = pkg_resources.get_distribution('ripozo').version


from ripozo.decorators import apimethod, translate
from ripozo.dispatch import adapters
from ripozo.viewsets import fields, restmixins
from ripozo.viewsets.relationships.list_relationship import ListRelationship
from ripozo.viewsets.relationships.relationship import Relationship
from ripozo.viewsets.resource_base import ResourceBase