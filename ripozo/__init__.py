"""
A python package for quickly building RESTful/Hypermedia/HATEOAS
applications in any web framework, with any database, using
any protocol.
"""

from ripozo.decorators import apimethod, translate
from ripozo.resources import fields, restmixins
from ripozo.resources.relationships.list_relationship import ListRelationship
from ripozo.resources.relationships.relationship import Relationship, FilteredRelationship
from ripozo.resources.resource_base import ResourceBase
from ripozo.resources.request import RequestContainer
from ripozo.utilities import picky_processor
