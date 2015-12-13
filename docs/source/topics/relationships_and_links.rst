Relationships and Links
=======================

Any good api is going to need references to
on resources to other references.  For example,
a parent and child resource would likely need
hypermedia references to the other.  The ``_relationships``
and ``_links`` class attributes on the ``ResourceBase`` subclass.
These attributes inform the resource instances how to construct
related and linked resources.

Example
"""""""

.. testcode:: relationship

    from ripozo import apimethod, Relationship, ResourceBase, RequestContainer


    class MyResource(ResourceBase):
        _relationships = (
            Relationship('related', relation='RelatedResource'),
        )

        @apimethod(methods=['GET'])
        def retrieve(cls, request, *args, **kwargs):
            properties = request.body_args
            return cls(properties=properties)


    class RelatedResource(ResourceBase):
        pks = ['id']

If we were to call the retrieve method now and inspect the
properties on the returned instance we would see that it no longer
contained the 'related' key or it's corresponding value.

.. doctest:: relationship

    >>> request = RequestContainer(body_args={'name': 'Yay!', 'related': {'id': 1}})
    >>> res = MyResource.retrieve(request)
    >>> res.properties
    {'name': 'Yay!'}
    >>> resource_tuple = res.related_resources[0]
    >>> print(resource_tuple.name)
    related
    >>> print(resource_tuple.resource.url)
    /related_resource/1
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

Cookbook
--------

.. testsetup:: queryargs, embedded, linktolist

    from ripozo import ResourceBase, apimethod, Relationship, ListRelationship, FilteredRelationship

A link with query args
^^^^^^^^^^^^^^^^^^^^^^

Sometimes, you want a link to have query args in the url.
A prime example of this is a next link when paginating.
You don't want to change the path but the query args should
be adjusted.  In this case, we can simply pass the a list
of arguments that should be query args.

.. testcode:: queryargs

    class MyResource(ResourceBase):
        _links = (
            Relationship('next', relation='MyResource', query_args=['page', 'count']),
        )

        @apimethod()
        def my_endpoint(cls, request):
            page = request.get('page', 1)
            count = request.get('count', 10)
            # get your resource list
            next = dict(page=page+1, count=count)
            meta=dict(links=dict(next=next))
            return cls(meta=meta)

Linked resources are created from the meta['links'] attribute on a resource.  This
means that we've given the next link the properties from the meta['links']['next']
dictionary.  Additionally, we've passed in ``['page', 'count']`` into the created linked
resource as query_args parameter in the constructor.  In other words, the next linked
resource would be constructed as follows: ``MyResource(properties=dict(page=page+1, count=count), query_args=['page', 'count'])``


.. doctest:: queryargs

    >>> from ripozo import RequestContainer
    >>> req = RequestContainer(query_args=dict(page=1, count=20))
    >>> resource = MyResource.my_endpoint(req)
    >>> print(resource.url)
    /my_resource
    >>> next_link = resource.linked_resources[0].resource
    >>> print(next_link.url)
    /my_resource?count=20&page=2

Emedding resources
^^^^^^^^^^^^^^^^^^

In this scenario, you want related resources to be fully embedded in the
requested resource.  Although what the representation depends on the adapter
used, it would look something like this:

.. code-block:: javascript

    {
        "parent": {
            "href": "http://myapi.io/parent_resource/1",
            "value": 1,
            "children": [
                {
                    "href": "http://myapi.io/child_resource/5",
                    "parent": "http://myapi.io/parent_resource/1",
                    "val": 2
                },
                {
                    "href": "http://myapi.io/child_resource/6",
                    "parent": "http://myapi.io/parent_resource/1",
                    "val": 2
                },
                {
                    "href": "http://myapi.io/child_resource/7",
                    "parent": "http://myapi.io/parent_resource/1",
                    "val": 2
                }
            ]
        }
    }

Assuming that we somehow constructed a dictionary representing the parent
dictionary above (for example from your manager) creating an embedded resource(s)
is very easy.

.. testcode:: embedded

    class ParentResource(ResourceBase):
        pks = ('id',)
        _relationships = (
            ListRelationship('children', relation='ChildResource', embedded=True),
        )

        @apimethod()
        def retrieve(cls, request):
            children = [dict(id=5, parent_id=1, val=2), dict(id=6, parent_id=1, val=2), dict(id=7, parent_id=1, val=2)]
            parent_props = dict(id=1, value=1, children=children)
            return cls(properties=parent_props)

    class ChildResource(ResourceBase):
        pks = ('id',)
        _relationships = (
            Relationship('parent', property_map=dict(parent_id='id'), relation='ParentResource'),
        )

In this case, we have embedded children relationship each of which has a relationship pointing back
to the parent. The key is the ``embedded=True`` which tells the adapter to include all of the properties.
If embedded was not equal to true we would only get the links to the resources in the response.

.. doctest:: embedded

    >>> from ripozo import RequestContainer
    >>> req = RequestContainer()
    >>> parent = ParentResource.retrieve(req)
    >>> children = parent.related_resources[0].resource
    >>> print(parent.related_resources[0].embedded)
    True
    >>> print(parent.url)
    /parent_resource/1
    >>> for child in children:
    ...     print(child.url)
    /child_resource/5
    /child_resource/6
    /child_resource/7
    >>> child = children[0]
    >>> childs_parent = child.related_resources[0].resource
    >>> print(childs_parent.url)
    /parent_resource/1
    >>> assert childs_parent.url == parent.url

..
    Link to child list
    ------------------

    What if instead of even embedding links to the children we simply
    wanted to point to a location where you could explicitly get the children
    for a specific parent.  It's generally considered more RESTful to hit
    point to an endpoint like ``'/children?parent_id=1'`` than ``'/parent/1/children'``.
    Fortunately this is extremely easy in ripozo with the :class: `FilteredRelationship` class.

    *NOTE* If you are using a manager than you can use the ``restmixins.Retrieve`` and/or
    ``restmixins.RetrieveList`` instead of explicitly declaring the retrieve methods.
    Makes it much faster to develop.

    .. testsetup:: linktolist

        class Parent(ResourceBase):
            pks = ('id',)
            relationships = (
                FilteredRelationship('children', relation='Child', property_map=dict(id='parent_id')),
            )

            @apimethod()
            def retrieve(cls, request):
                return cls(properties=dict(id=request.get('id')))

        class Child(ResourceBase):
            pks = ('id',)

            @apimethod(no_pks=True)
            def retrieve_list(cls, request):
                # get the children using the query args as filters
                # you would actually populate this of course
                children = {'children': []}
                return cls(properties=children)


    .. doctest:: linktolist

        >>> from ripozo import RequestContainer
        >>> req = RequestContainer(url_params=dict(id=5))
        >>> parent = Parent.retrieve(req)
        >>> print(parent.url)
        /parent/5
        >>> children = parent.related_resources[0].resource
        >>> print(children.url)
        /child?parent_id=5

Relationships API
-----------------

.. autoclass:: ripozo.resources.relationships.relationship.Relationship
    :members:
    :special-members:

.. autoclass:: ripozo.resources.relationships.list_relationship.ListRelationship
    :members:
    :special-members:

.. autoclass:: ripozo.resources.relationships.relationship.FilteredRelationship
    :members:
    :special-members:
