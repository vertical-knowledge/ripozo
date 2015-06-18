CHANGELOG
=========

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
