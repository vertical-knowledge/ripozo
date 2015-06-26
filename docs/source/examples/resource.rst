Resource Examples
=================

URL construction
^^^^^^^^^^^^^^^^

.. testsetup:: basic_url

    from ripozo import ResourceBase

    class MyResource(ResourceBase):
        pks = ['id']


.. doctest:: basic_url

    >>> print(MyResource.base_url)
    /my_resource/<id>
    >>> resource = MyResource(properties={'id': 1})
    >>> print(resource.url)
    /my_resource/1

URL construction 2
^^^^^^^^^^^^^^^^^^

.. testsetup:: url2

    from ripozo import ResourceBase

    class MyResource(ResourceBase):
        namespace = '/api'
        pks = ['id']
        resource_name = 'resource/'


.. doctest:: url2

    >>> print(MyResource.base_url)
    /api/resource/<id>
    >>> resource = MyResource(properties={'id': 1})
    >>> print(resource.url)
    /api/resource/1

Minimal Request
^^^^^^^^^^^^^^^

.. testsetup:: minimal

    from ripozo import RequestContainer, ResourceBase, apimethod

    class MyResource(ResourceBase):
        namespace = '/api'
        pks = ['id']
        resource_name = 'resource'

        @apimethod(methods=['GET'])
        def hello_world(cls, request):
            id = request.url_params['id']
            return cls(properties={'id': id, 'hello': 'world'})


.. doctest:: minimal

    >>> request = RequestContainer(url_params={'id': 2})
    >>> resource = MyResource.hello_world(request)
    >>> print(resource.url)
    /api/resource/2
    >>> resource.properties
    {'id': 2, 'hello': 'world'}

Using Fields
^^^^^^^^^^^^

.. testsetup:: fields

    from ripozo import apimethod, translate, fields, ResourceBase

    class MyResource(ResourceBase):
        namespace = '/api'
        pks = ['id']
        resource_name = 'resource'

        @apimethod(methods=['GET'])
        @translate(fields=[fields.IntegerField('id', required=True)], validate=True)
        def hello_world(cls, request):
            id = request.url_params['id']
            return cls(properties={'id': id, 'hello': 'world'})


.. doctest:: fields
    :options: IGNORE_EXCEPTION_DETAIL

    >>> from ripozo import RequestContainer
    >>> request = RequestContainer()
    >>> resource = MyResource.hello_world(request)
    Traceback (most recent call last):
    ...
    ValidationException: The field "id" is required and cannot be None

Relationships
^^^^^^^^^^^^^

.. testsetup:: relationship

    from ripozo import apimethod, translate, fields, ResourceBase, Relationship

    class MyResource(ResourceBase):
        namespace = '/api'
        pks = ['id']
        resource_name = 'resource'
        _relationships = [
            Relationship('related', relation='RelatedResource')
        ]

        @apimethod(methods=['GET'])
        @translate(fields=[fields.IntegerField('id', required=True)], validate=True)
        def hello_world(cls, request):
            id = request.url_params['id']
            return cls(properties={'id': id, 'hello': 'world'})

    class RelatedResource(ResourceBase):
        pks = ['pk']


.. doctest:: relationship

    >>> properties = dict(id=1, related=dict(pk=2))
    >>> resource = MyResource(properties=properties)
    >>> resource.properties
    {'id': 1}
    >>> print(resource.related_resources[0].name)
    related
    >>> related_resource = resource.related_resources[0].resource
    >>> related_resource.properties
    {'pk': 2}
    >>> print(related_resource.url)
    /related_resource/2
