Fields, Translation, and Validation
===================================

This topic describes how to translate and validate parameters
from a request.

Translation is the process of converting the incoming parameter (typically
a string) into the desired ``type``.  For example, there may be a
request such as the following: ``http://mydomain.com/resource?count=20``.
The count parameter would be a string, however we would want to use
it as an integer.  Therefore, we would cast/translate it to an integer.
This can encapsulate more than just casting (e.g. turning a JSON string
into a ``dict``.

Validation takes the translated parameter and ensures that it fulfills
a certain set of expectations.  In the previous example, we may wish
to validate that the ``count`` query argument is always greater than 0.

Simple Example
--------------

This example demonstrates how to perform simple translation and
validation on an count parameter

.. testsetup:: *

    from ripozo import translate, fields, apimethod, ResourceBase, RequestContainer

.. testcode:: simpleexample

    from ripozo import translate, fields, apimethod, ResourceBase, RequestContainer

    class MyResource(ResourceBase):

        @apimethod(methods=['GET'])
        @translate(fields=[fields.IntegerField('count', minimum=1)], validate=True)
        def hello(cls, request):
            count = request.get('count')
            return cls(properties=dict(count=count))

The ``translate`` decorator translates the inputs using a series of fields.  If
we pass ``validate=True`` to the ``translate`` decorator, it will perform validation
as well.  The list of fields passed to the ``fields`` parameter must all be instances
of :py:class:`BaseField` .  ``BaseField`` classes perform
the actual translation and validation for a given field.

.. doctest:: simpleexample

    >>> req = RequestContainer(query_args=dict(count='3'))
    >>> res = MyResource.hello(req)
    >>> res.properties['count'] == 3
    True
    >>> req = RequestContainer(query_args=dict(count='0'))
    >>> res = MyResource.hello(req)
    Traceback (most recent call last):
        ...
    ValidationException: The field "count" is required and cannot be None
    >>> req = RequestContainer(query_args=dict(count='not an integer'))
    >>> res = MyResource.hello(req)
    Traceback (most recent call last):
        ...
    TranslationException: Not a valid integer type: not an integer

We can see that the string is appropriately cast in the first attempt and passes validation.
The second example raises a ``ValidationException`` because it was id<1 which
we specified as the minimum.  Finally, the last example raises a TranslationException
because the ``id`` parameter was not a valid integer.

Specifying the location
-----------------------

By default, the ``translate`` decorator will look in the url parameters, query arguments
and body arguments when finding the parameter to check.  For example,
the following still works

.. doctest:: simpleexample

    >>> req = RequestContainer(body_args=dict(count='3'))
    >>> res = MyResource.hello(req)
    >>> res.properties['count'] == 3
    True

However, sometimes we may require that a parameter is only allowed in a
specific location.  With ripozo, this is very simple.

.. testcode:: simpleexample

    from ripozo.resources.constants.input_categories import QUERY_ARGS

    # we'll declare the fields here for cleanliness
    # Note the arg_type parameter which specifies to
    # only look in the query args for this field
    hello_fields = [fields.IntegerField('count', required=True, minimum=1, arg_type=QUERY_ARGS)]

    class MyResource(ResourceBase):

        @apimethod(methods=['GET'])
        @translate(fields=hello_fields, validate=True)
        def hello(cls, request):
            count = request.get('count')
            return cls(properties=dict(count=count))

The previous example, will no longer work since the field is
only allowed to be from the query arguments.

.. doctest:: simpleexample

    >>> req = RequestContainer(body_args=dict(count='3'))
    >>> res = MyResource.hello(req)
    Traceback (most recent call last):
        ...
    ValidationException: The field "count" is required and cannot be None
    >>> req = RequestContainer(query_args=dict(count='3'))
    >>> res = MyResource.hello(req)
    >>> res.properties['count'] == 3
    True

With this method, we could even translate and validate two fields with the
same name as long as they are in different locations.

Creating special fields
-----------------------

While there are plenty of fields available in :ref:`all-fields`,
sometimes, you need something more specific.  In this example we'll show you how
to create an email validation field.

To create a new field, you simply need to inherit from :py:class:`ripozo.resources.fields.base.BaseField` and
override the necessary methods, in particular the ``_translate`` and ``_validate``
methods.

.. testcode:: newfield

    from ripozo import fields
    from ripozo.exceptions import ValidationException

    class EmailField(fields.BaseField):
        def _validate(self, obj, **kwargs):
            # perform the standard validation such as whether it is required.
            obj = super(EmailField, self)._validate(obj, **kwargs)
            if obj is None:  # In case it wasn't a required field.
                return obj
            if '@' not in obj:
                raise ValidationException('"{0}" is not a valid email address'.format(obj))
            return obj

We could then test this by running the following

.. doctest:: newfield

    >>> field = EmailField('email_address', required=True)
    >>> field.translate('some@email.com', validate=True)
    'some@email.com'
    >>> field.translate('not an email', validate=True)
    Traceback (most recent call last):
        ...
    ValidationException: "not an email" is not a valid email address

We can then use this new field like the ``IntegerField`` we used previously.



API Documentation
=================

Translation and Validation Decorators
-------------------------------------

.. autoclass:: ripozo.decorators.translate
    :members:
    :special-members:

.. autoclass:: ripozo.decorators.manager_translate
    :members:
    :special-members:

.. _all-fields:

Field types
-----------

.. automodule:: ripozo.resources.fields.common
    :members:
    :special-members:

.. automodule:: ripozo.resources.fields.base
    :members:
    :special-members:
