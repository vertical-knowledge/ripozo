Resource Example
================

.. code-block:: python

    from ripozo.viewsets.resource_base import ResourceBase

    class MyResource(ResourceBase):
        _pks = ['id']

.. code-block:: python

    >>> MyResource.base_url
    '/my_resource/<id>'
    >>> resource = MyResource(properties={'id': 1})
    >>> resource.url
    '/my_resource/1'


.. code-block:: python

    from ripozo.viewsets.resource_base import ResourceBase

    class MyResource(ResourceBase):
        _namespace = '/api'
        _pks = ['id']
        _resource_name = 'resource'


.. code-block:: python

    >>> MyResource.base_url
    '/api/resource/<id>'
    >>> resource = MyResource(properties={'id': 1})
    >>> resource.url
    '/api/resource/1'


.. code-block:: python

    from ripozo.viewsets.request import RequestContainer

    from ripozo.decorators import apimethod
    from ripozo.viewsets.resource_base import ResourceBase

    class MyResource(ResourceBase):
        _namespace = '/api'
        _pks = ['id']
        _resource_name = 'resource'

        @apimethod(methods=['GET'])
        def hello_world(cls, request):
            id = request.body_args['id']
            return cls(properties={'id': id, 'hello': 'world'})


.. code-block:: python

    >>> from ripozo.viewsets.request import RequestContainer
    >>> request = RequestContainer(body_args={'id': 2})
    >>> resource = MyResource.hello_world(request)
    >>> resource.url
    '/api/resource/2'
    >>> resource.properties
    {'id': 2, 'hello': 'world'}


.. code-block:: python

    from ripozo.decorators import apimethod, translate
    from ripozo.viewsets.fields.common import IntegerField
    from ripozo.viewsets.resource_base import ResourceBase

    class MyResource(ResourceBase):
        _namespace = '/api'
        _pks = ['id']
        _resource_name = 'resource'

        @apimethod(methods=['GET'])
        @translate(fields=[IntegerField('id', required=True)], validate=True)
        def hello_world(cls, request):
            id = request.body_args['id']
            return cls(properties={'id': id, 'hello': 'world'})


.. code-block:: python

    >>> from ripozo.viewsets.request import RequestContainer
    >>> request = RequestContainer()
    >>> resource = MyResource.hello_world(request)
    ...
    ripozo.exceptions.ValidationException: The field "id" is required and cannot be None


.. code-block:: python

    from ripozo.decorators import apimethod, translate
    from ripozo.viewsets.fields.common import IntegerField
    from ripozo.viewsets.relationships import Relationship
    from ripozo.viewsets.resource_base import ResourceBase

    class MyResource(ResourceBase):
        _namespace = '/api'
        _pks = ['id']
        _resource_name = 'resource'
        _relationships = [
            Relationship('related', relation='RelatedResource')
        ]
        # ...

    class RelatedResource(ResourceBase):
        _pks = ['pk']


.. code-block:: python

    >>> properties = dict(id=1, related=dict(pk=2))
    >>> resource = MyResource(properties=properties)
    >>> resource.properties
    {'id': 1}
    >>> resource.relationships
    [(<example.RelatedResource object at ...>, u'related', False)]
    >>> related_resource = resource.relationships[0][0]
    >>> related_resource.properties
    {'pk': 2}
    >>> related_resource.url
    u'/related_resource/2'
