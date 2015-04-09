
.. _preprocessors and postprocessors:

Tutorial Part 2: Preprocessors and Postprocessors
=================================================

Sometimes, you want to run a certain piece of code before/after every
request to a resource.  For example, maybe the resource is only accessible
to authenticated users. This can be done easily with preprocessors and postprocessors.
The preprocessors and postprocessors lists are the functions that are called before
and after the ``apimethod`` decorated function runs.  They are run in the order in which
they are described in the list.

.. code-block:: python

    def pre1(cls, request):
        print('In pre1')

    def pre2(cls, request):
        print('In pre2')

    def post1(cls, request, resource):
        print('In post1')

    class MyResource(ResourceClass):
        _preprocessors = [pre1, pre2]
        _postprocessors = [post1]

        @apimethod(methods=['GET'])
        def say_hello(cls, request):
            print('In say_hello')
            return cls(properties=dict(hello='world'))

.. code-block:: python

    >>> MyResource.say_hello(None)
    In pre1
    In pre2
    In say_hello
    In post1

These can be used to perform any sort of common functionality across
all requests to this resource.  Preprocessors always get the class as
the first argument and the request as the second.  Postprocessors get an
additional resource argument as the third.  The resource object is the return
value of the apimethod.

:doc:`tutorial_part_3`
