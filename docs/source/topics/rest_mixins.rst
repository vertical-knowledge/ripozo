Rest Mixins
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

All of the rest mixins are subclasses of ResourceBase.  The following
base mixins are available in addition to various combinations of them.
They can be mixed and matched as you please.

- Create
- Retrieve
- RetrieveList
- Update
- Delete
- CRUD (Create, Retrieve, Update, Delete)
- CRUDL (Create, Retrieve, RetrieveList, Update, Delete)

.. code-block:: python

    from mymanagers import MyManager

    from ripozo import ListRelationship, Relationship, restmixins

    class MyResourceList(restmixins.CRUDL):
        _resource_name = 'resource'
        _manager = MyManager
        _pks = ('id',)


 Rest Mixins API
 ---------------

 .. automodule:: ripozo.resources.restmixins
    :members:
