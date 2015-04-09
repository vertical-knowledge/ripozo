CRUD Basics
===========

We get it.  Most of the time, you want some basic
CRUD+L (Create, Retrieve, Update, Delete and Lists).
Also, you don't want to have to write basic code
for every single resource.  Ripozo, implements the basics
for you so that you don't have to rewrite them everytime and
can focus on the interesting parts of your api.

.. code-block:: python

    from mymanagers import MyManager

    from ripozo.viewsets.restmixins import Create

    class MyResource(Create):
        _resource_name = 'my_resource'
        _manager = MyManager

This would create a endpoint '/my_resource' that if posted
to would create a resource using the ``MyManager().create``
method.  It would then serialize and return an instance of MyResource.

All of the rest mixins are subclasses of ResourceBase.  In addition
to the Create mixin the following are available:

- Create
- Retrieve
- Update
- Delete
- RetrieveList
- CreateRetrieveList
- RetrieveUpdate
- RetrieveUpdateDelete
- RetrieveDelete
- UpdateDelete


