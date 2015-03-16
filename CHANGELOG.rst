0.1.15 (unreleased)
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
