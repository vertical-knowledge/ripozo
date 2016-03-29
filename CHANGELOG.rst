Changelog
`````````

1.x Releases
~~~~~~~~~~~~

1.3.1 (unreleased)
==================

- WSGI integrations added to ``ripozo.wsgi`` including mechanisms for directly parsing the request body, query args, and headers
- Deprecated ``format_request`` on adapters in favor of parsing directly from the wsgi environment.  This gives the end developer much more flexibility in choosing how to read in requests.  The wsgi package should make simple integrations simple.
- ``construct_request_from_wsgi_environ`` now required for adapters or a warning will be raised.  In v2.0.0 this will raise an exception
- Added ``construct_request`` method to ``DispatcherBase``.  This method takes a wsgi environ and constructs a RequestContainer from it using the appropriate adapter based on the Content-Type header


1.3.0 (2016-02-16)
==================

- New Field class.  The ``BaseField`` class is now deprecated.  The switch is largely backwards compatible if you are not using private functions.  If you are inheriting from the ``BaseField`` directly you will need to update to use the new ``ripozo.resources.fields.field.Field`` class.  The change should be transparent.
- Validation helpers.  A new module that includes helper functions for common validation scenarios.  ``ripozo.resources.fields.validations``
- The ``BaseField`` is deprecated and will be removed in v2.0.0


1.2.3 (2015-11-22)
==================

- Bug fix for JSONAPI adapter that occurred when a resource with no primary keys was passed to the adapter causing it to break


1.2.2 (2015-11-22)
==================

- The HalAdapter now includes fully qualified resources in the _embedded property.  There is no difference in how top-level vs embedded resources are constructed at this point.


1.2.1 (2015-11-20)
==================

- Fixed setup.py to only include ripozo packages.


1.2.0 (2015-11-20)
==================

- Added `remove_properties` attribute to `Relationship` instantiation.  This allows a user to keep properties in both the parent and the child such as passing a parent's id to the child while keeping it in its properties.
- Added `FilterRelationship` class which provides a shortcut to creating Relationships that point to a filtering against a list of resources.
- Added `manager_translate` decorator which will replace the `translate` decorator when using manager generated fields to translate and decorate an @apimethod.  Using `translate` for manager_fields will be deprecated in v2.0


1.1.1 (2015-11-04)
==================

- Moved up some imports for ease of use


1.1.0 (2015-08-26)
==================

- Bug fix for BasicJSONAdapter.
- Base adapter got a format_request method that must be called by the dispatcher.  This allows the adapter to appropriately reformat the request into a ripozo acceptable format.
- Warnings raised in base adapter's format_request and format_exception since these must be implemented by the adapter in version 2.0.0
- All adapters explicitly override format_exception and format_request
- Fixed `join_url_parts` bug so that responses always return unicode objects (`str` type in python 3)
- Added an adapter that meets the `JSON API specification <http://jsonapi.org/format/>`_


1.0.0 (2015-06-30)
==================

- Nothing changed yet.

0.x Releases
~~~~~~~~~~~~

1.0.0b1 (2015-06-29)
====================

- Fixed bug in url for the resource instance returned by the RetrieveList mixin.
- manager_field_validators attribute in @translate decorator removed.  It's now expected that you explicitly call translate_fields in your method if you wish to translate fields in an inheritable class apimethod
- Warnings raised when a class registered with a dispatcher has a relationship/link with a relation that does not exist in the ResourceMetaClass registry.
- renamed BoringJSONAdapter to BasicJSONAdapter
- Templated relationships now available.
- Route extensions available on ResourceBase instances.  This allows a user to append part of a url to a resource base so that the .url property renders properly.  This is helpful when route is defined on an apimethod.


0.6.1 (2015-06-24)
==================

- Added valid_fields static method to BaseManager which is helper for getting valid fields.


0.6.0 (2015-06-24)
==================

- pylint shit.
- Moved dispatch_base up and removed dispatch package
- Moved manager_base and removed manager package.
- Added append_slash class attribute to ResourceBase. Setting this attribute to True automatically appends a slash to the end of the base_url and base_url_sans_pks.  Defaults to False.


0.5.0 (2015-06-18)
==================

- Renamed viewsets package to resources
- Many underscore fields were removed with the exception of _relationships and _links
- Fields default to checking the Query string, request body and url parameters for argument if no arg_type is specified.
- Query args can be specified in relationships.  Every argument available will be appended to the query string
- query args on a resource is now a list that simply pulls from the properties.
- Removed translate method from request container.  Instead the request object is now injected into the translate_fields method from ripozo.viewsets.fields.base module


0.4.0 (2015-06-07)
==================

- Using Accept-Types instead of Content-Type.


0.4.0b1 (2015-06-05)
====================

- RetrieveList now compatible with Single resource rest mixins
- Added RetrieveRetrieveList restmixin.
- Relationships now take a no pks parameter which specifies that the resource in question should not use the pks (helpful for RetrieveRetrieveList and such)
- Fixed bug in DictField that removed key-value pairs not explicitly specified.
- Added update_fields class property to Base Manager.


0.3.1 (2015-05-29)
==================

- Added DictField to top level import in fields.


0.3.0 (2015-05-29)
==================

- Fixes for RetrieveRetrieveList bad translation.
- Added DictField which can translate and validate dictionary fields (and their subfields)


0.2.1 (2015-05-08)
==================

- Endpoints that are generated now use "<class name>__<function_name>" as the default endpoint name
- Removed check fore the base rest endpoint.  This doesn't take into account dispatchers having url_prefixes
- Added get method to RequestContainer which searches through the url_params, query_args, and then the body_args to find a value
- Added create_fields property to the BaseManager.  This allows a user to specify which fields are valid for creation.
- related resources and linked resources named tuples

0.2.0 (2015-04-28)
==================

- Removed ripozo_tests dependency.  It is now included in the package itself.


0.1.26 (2015-04-23)
===================

- Added base_url_sans_pks classproperty to ResourceBase
- Create is now an individual resource rather than a list resource
- Added CreateRetrieve, CreateRetrieveUpdate, andCreateRetrieveUpdateDelete mixins
- Removed CreateRetrieveList mixin


0.1.25 (2015-04-16)
===================

- Overhauled how links and relationships are generated
- Lots of bugs
- Added include_relationships keyword argument to ResourceBase __init__ for performance reasons


0.1.24 (2015-04-13)
===================

- Nothing changed yet.


0.1.23 (2015-04-13)
===================

- Changed location of classproperty decorator from ``ripozo.utilities`` to ``ripozo.decorators``
- Fixed bug with wrapping _apiclassmethod decorated functions.


0.1.22 (2015-04-10)
===================

- Fixed error with formatting exceptions


0.1.21 (2015-04-07)
===================

- Added links
- Added _list_fields attribute to BaseManager for more efficient querying when necessary
- Moved getting the adapter class based on the format type in the dispatcher to its own method.


0.1.20 (2015-03-24)
===================

- Fields no longer have a default.
- Adapter.extra_headers returns a dictionary instead of a list
- Fields can specify an error message.
- ListField added
- Fixed deep inheritance issue with translate decorator.
- Added the name of the relationship as an item in the rel list in the SIREN adapter.


0.1.19 (2015-03-16)
===================

- Endpoint name


0.1.18 (2015-03-16)
===================

- Fixed bug with RetrieveRetrieveList mixin
- Added ``picky_processor`` which specifically includes processors to include or exclude.
- pre and post processors now get the name of the function being called. before running


0.1.17 (2015-03-16)
===================

- Fucked up...


0.1.16 (2015-03-16)
===================

- Fixed the bug where inheritance of abstract methods resulted in mutable common endpoint_dictionaries
- endpoint_dictionary is now a method and not a property


0.1.15 (2015-03-16)
===================

- Fixed bug that resulted in multiple forward slashes in a row on a url


0.1.14 (2015-03-16)
===================

- Added method to RequestContainer object
- Imported Relationship and ListRelationship into relationships.__init__.py module for more intuitive access
- Imported HtmlAdapter to adapters.__init__.py for more intuitive imports.
- Including html adapter templates in package


0.1.13 (2015-03-14)
===================

- Added generic CRUD+L mixins.  These are included merely for convience
- Required fields validation can be skipped.  In other words, you can now specify that a field does not need to be present when validating


0.1.12 (2015-03-14)
===================

- Code cleanup


0.1.11 (2015-03-08)
===================

* Some updates to the release process.


0.1.10 (2015-03-08)
===================

* Started using zest.releaser for managing releases.
* Added ``register_resources`` method to the DispatcherBase class
