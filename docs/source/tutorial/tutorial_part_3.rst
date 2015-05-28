Tutorial Part 4: Relationships and Links
========================================

Any good api is going to need references to
on resources to other references.  For example,
a parent and child resource would likely need
hypermedia references to the other.  The ``_relationships``
and ``_links`` class attributes on the ``ResourceBase`` subclass.
These attributes inform the resource instances how to construct
related and linked resources.

Example
"""""""

.. code-block:: python

    from ripozo import apimethod, Relationship, ResourceBase


    class MyResource(ResourceBase):
        _relationships = {
            'related_resource': Relationship('related', relation='RelatedResource')
        }

        @apimethod(methods=['GET'])
        def retrieve(cls, request, *args, **kwargs):
            properties = request.body_args
            return cls(properties=properties)


    class RelatedResource(ResourceBase):
        pks = ['id']

If we were to call the retrieve method now and inspect the
properties on the returned instance we would see that it no longer
contained the 'related' key or it's corresponding value.

.. code-block:: python

    >>> from ripozo import RequestContainer
    >>> request = RequestContainer({'name': 'Yay!', 'related': {'id': 1}})
    >>> res = MyResource.retrieve(request)
    >>> res.properties
    {'name': 'Yay!'}
    >>> resource_tuple = res.related_resources[0]
    >>> print(resource_tuple.name)
    'related'
    >>> print(resource_tuple.resource.url)
    '/api/related/1'
    >>> print(resource_tuple.resource.properties)
    {'id': 1}

Instead the relationship 'related_resource' popped the
value with the key 'related' from the properties dict
and passed the properties to the instantiatior for the RelatedResource.
The RelatedResource now exists in the ``res.relationships`` list.
Adapters can properly retrieve urls using the resource object and
format them appropriately.

Links vs Relationships
----------------------

The links and the relationships attributes both use the ``Relationship``
and ``ListRelationship``.  In fact in many aspects they are extraordinarily
similiar.  They both construct resources.  The main difference is in how they
are constructed (links use the ``resource.meta['links']`` dictionary and
relationships directly access the properties) and their fundamental meaning.
A relationship is effectively a part of the resource itself.  For example,
a child and parent relationship.  The child is directly part of the parent.
A link would be closer to a sibling.  They may be a 'next' link which points
to the next sibling from a child resource.  However, there is no next attribute
directly on the child.  A common use case for links is describing next and previous
links on paginated lists.  The resource is the list and the next and previous is
not actually an attribute of the resource.  Instead it is meta information about
the resource.

:doc:`tutorial_part_4`
