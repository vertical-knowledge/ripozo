from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from ripozo import ResourceBase, apimethod

class MyResource(ResourceBase):
    _namespace = '/api'
    _resource_name = 'resource'

    @apimethod(methods=['GET'])
    def say_hello(cls, request):
        return cls(properties=request.body_args)

class MyOtherResource(ResourceBase):
    _namespace = '/api'
    _resource_name = 'resource2'
    _pks = ['id', 'pk']

    @apimethod(methods=['GET'])
    def say_hello(cls, request):
        props = request.body_args
        props.update(request.url_params)
        return cls(properties=props)


if __name__ == '__main__':
    from ripozo import RequestContainer

    request = RequestContainer(body_args={'say': 'hello'})
    resource = MyResource.say_hello(request)

    # Prints '/api/resource'
    print(MyResource.base_url)

    # Prints {'say': 'hello'}
    print(resource.properties)

    request = RequestContainer(url_params={'id': 1, 'pk': 2}, body_args={'say': 'hello'})
    other_resource = MyOtherResource.say_hello(request)

    # Prints '/api/resource2/<id>/<pk>
    print(MyOtherResource.base_url)

    # prints '/api/resource2/1/2
    print(other_resource.url)

    # prints the url parameters and body args
    # {'id': 1, 'pk': 2, 'say': 'hello'}
    print(other_resource.properties)
