# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function
# from __future__ import unicode_literals
#
# from ripozo.exceptions import BaseRestEndpointAlreadyExists
# from ripozo.viewsets.relationships import ListRelationship, Relationship
# from ripozo.viewsets.resource_base import ResourceBase
#
# import mock
#
#
# class FakeResources(object):
#     def __init__(self):
#         self._resource = None
#         self._related_resource = None
#
#     @property
#     def resource(self):
#         try:
#             class FakeResource(ResourceBase):
#                 _resource_name = 'fake'
#             self._resource = FakeResource
#         except BaseRestEndpointAlreadyExists:
#             pass
#         return self._resource
#
#     @property
#     def related_resource(self):
#         try:
#             class FakeResource(ResourceBase):
#                 _resource_name = 'fake_related'
#             self._related_resource = FakeResource
#         except BaseRestEndpointAlreadyExists:
#             pass
#         return self._related_resource
#
#     @property
#     def simple(self):
#         props = dict(value='something', anothervalue='something else', final_value=1)
#         return self.resource(properties=props)
#
#     @property
#     def simple_single_related(self):
#         resource = self.resource
#         resource._relationships = {
#             'relationship': Relationship(property_map=dict(related_id='id'))
#         }
#         related = self.related_resource
#         related._pks = ['id']
#         props = dict(value='something', related_id)
