from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo import ResourceBase, apimethod, RequestContainer, picky_processor


def pre1(cls, function_name, request):
    print('In pre1')

def pre2(cls, function_name, request):
    print('In pre2')

def post1(cls, function_name, request, resource):
    print('In post1')

class MyResource(ResourceBase):
    # preprocessors run before the apimethod
    _preprocessors = [pre1, pre2]
    # and postprocessors run after.
    _postprocessors = [post1]

    @apimethod(methods=['GET'])
    def say_hello(cls, request):
        print('hello')
        return cls(properties=dict(hello='world'))


class PickyResource(ResourceBase):
    # only runs for the specified methods
    _preprocessors = [picky_processor(pre1, include=['say_hello']),
                      picky_processor(pre2, exclude=['say_hello'])]

    @apimethod(methods=['GET'])
    def say_hello(cls, request):
        print('hello')
        return cls(properties=dict(hello='world'))

    @apimethod(route='goodbye', methods=['GET'])
    def say_goodbye(cls, request):
        print('goodbye')
        return cls(properties=dict(goodbye='world'))


if __name__ == '__main__':
    req = RequestContainer()
    MyResource.say_hello(req)
    # Prints:
    # In pre1
    # In pre2
    # hello
    # In post1

    PickyResource.say_hello(req)
    # Prints
    # In pre1
    # hello

    PickyResource.say_goodbye(req)
    # Prints:
    # In pre2
    # goodbye
