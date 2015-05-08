from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo import ResourceBase, apimethod, Relationship

class MyResource(ResourceBase):
    _namespace = '/api'
    _resource_name = 'resource'
    _relationships = [
        Relationship('related', relation='RelatedResource')
    ]

    @apimethod(methods=['GET'])
    def say_hello(cls, request):
        return cls(properties=request.body_args)

class RelatedResource(ResourceBase):
    _namespace = '/api'
    _resource_name = 'related'
    _pks = ['id']


if __name__ == '__main__':
    from ripozo import RequestContainer

    request = RequestContainer(body_args={'say': 'hello', 'related': {'id': 1}})
    resource = MyResource.say_hello(request)

    # prints {'say': 'hello'}
    print(resource.properties)

    resource_tuple = resource.related_resources[0]

    # prints 'related'
    print(resource_tuple.name)

    # prints '/api/related/1'
    print(resource_tuple.resource.url)

    # prints {'id': 1}
    print(resource_tuple.resource.properties)
