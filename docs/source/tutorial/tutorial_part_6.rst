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

This is a good point to investigate another aspect of ripozo's philosophy.
Ripozo takes the approach that a list of resources is a different resource
than the individual resources.  The main indicator of this is that typically
they will have different endpoints (A list might be ``/api/resource`` while
the individual would be ``/api/resource/<id>``). In this line of thought,
the Create would belong with the List because you are adding a resource
to the list resource.

The outcome of this decision is that to implement full CRUD+L you need to
actually create two resources.

.. code-block:: python

    from mymanagers import MyManager

    from ripozo.viewsets.relationships import ListRelationship, Relationship
    from ripozo.viewsets.restmixins import CreateRetrieveList, RetrieveUpdateDelete


    class MyResourceList(CreateRetrieveList):
        _resource_name = 'resource'
        _manager = MyManager
        # This is needed so that the individual resources can be properly loaded
        _relationships = {'my_resources': ListRelationship('my_resource', relation='MyResource')}
        # This is for the created so that it can link to the created resource.
        _links = {'created': Relationship(name='created', relation='MyResource')}


    class MyResource(RetrieveUpdateDelete):
        _resource_name = 'resource'
        _manager = MyManager
        _pks = ['id']

