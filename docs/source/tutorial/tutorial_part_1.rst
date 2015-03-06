Tutorial Part 1: Resources
==========================

Resources are the core of ripozo.  These define
what can be accessed and the actions you can
perform on those resources.  They are designed to be
common across all ripozo integrations.  In other words,
if they are designed correctly, a resource should be
able to be plugged into different web frameworks and managers
should be able to be plugged in and out.

.. _minimal resource:

Minimal Application
-------------------

.. code-block:: python

   from ripozo import ResourceBase, apimethod


   class MyResource(ResourceBase):

       @apimethod(methods=['GET'])
       def say_hello(cls, request):
           return cls(properties=dict(hello='world'))


That is your most basic resource.  It simply has one method available
to act on the resource.  The :class:`ripozo.decorators.apimethod` decorator indicates which
methods are going to be exposed by the api.  If we were to add another
method, that was not decorated by the ``@apimethod`` that method
would not be exposed in the api

.. code-block:: python

   class MyResource(ResourceBase):

       # This method is exposed by the api
       @apimethod(methods=['GET'])
       def say_hello(cls, request):
          return cls(properties=cls.get_properties())

       # This method will not be exposed
       @classmethod
       def get_properties():
          return dict(hello='world')

You'll notice that methods decorated by ``apimethod`` are class methods.
Additionally, an apimethod must always return an instance of a ResourceBase
subclass.  ResourceBase subclass instances, such as MyResource instances,
describe what the resource being returned is.  They describe both the properties
of the resource and the actions available to perform on that resource.

.. _resource urls:

What about the url?
-------------------

So how would you access this resource?  The first step would be to register
it with a dispatcher (which we will get into in the next chapter).  However,
once you registered the url, you would be able to access the resource by using
the "/my_resource" url with the GET http verb.  There are two major parts to the
url for a resource.

The first is the class property ``base_url``.  The ``ResourceBase.base_url`` specifies
the common base url for all actions on the resource.  It is constructed by taking
the ``ResourceBase.resource_name`` class property and appending it the the
``ResourceBase.namespace`` class property [#]_.  Additionally, the ``ResourceBase.pks``
are taken and each one is added as a url_parameter [#]_.

.. code-block:: python

    class MyResource(ResourceBase):
        _resource_name = 'resource'
        _namespace = '/api'
        _pks = ['id', 'secondary']

.. code-block:: python

    >>> MyResource.base_url
    '/api/resource/<id>/<secondary>'

If you take a MyResource instance and get the ``url`` property on
it, you will receive a valid url rather than just a template.  It will take
the properties that match the pks and plug them into the ``base_url`` template.

.. code-block:: python

    >>> resource = MyResource(properties=dict(id=3233, secondary='something'))
    >>> resource.url
    '/api/resource/3233/something'

.. _preprocessors and postprocessors:

Preprocessors and Postprocessors
--------------------------------

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

:doc:`tutorial_part_2`


.. [#] In ripozo, whenever urls are constructed, they are joined with a '/'.
   However, it will not allow multiple slashes in a row.  For example, if you
   had a namespace of '/api/' and resource_name of '/myresource', it would
   still use '/api/myresource' as the url.  You can view more details
   at :func:`ripozo.utilities.join_url_parts`

.. [#] Url parameters in the base_url are indicating a a part of the whole path.
   Additionally, they are wrapped in angle brackets.  For example, if you had the
   ``_resource_name = 'my_resource'`` and the ``_pks = ['id', 'secondary']``  The base url would
   be ``'/my_resource/<id>/<secondary>``