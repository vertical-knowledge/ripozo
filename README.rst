ripozo
======

.. image:: https://travis-ci.org/vertical-knowledge/ripozo.svg?branch=master&style=flat
    :target: https://travis-ci.org/vertical-knowledge/ripozos
    :alt: test status

.. image:: https://coveralls.io/repos/vertical-knowledge/ripozo/badge.svg?branch=master&style=flat
    :target: https://coveralls.io/r/vertical-knowledge/ripozo?branch=master
    :alt: test coverage

.. image:: https://readthedocs.org/projects/ripozo/badge/?version=latest&style=flat
    :target: https://ripozo.readthedocs.org/
    :alt: documentation status

..
    .. image:: https://pypip.in/version/ripozo/badge.svg?style=flat
        :target: https://pypi.python.org/pypi/ripozo/
        :alt: current version

..
    .. image:: https://pypip.in/download/ripozo/badge.png?style=flat
        :target: https://pypi.python.org/pypi/ripozo/
        :alt: PyPI downloads

.. image:: https://img.shields.io/pypi/dm/ripozo.svg?style=flat
    :target: https://pypi.python.org/pypi/ripozo/
    :alt: python versions
    
    
    
.. image:: https://img.shields.io/github/stars/vertical-knowledge/ripozo.svg?style=flat
    :target: https://github.com/vertical-knowledge/ripozo/
    :alt: stars

A pluggable tool for quickly and efficiently creating web apis.
In the modern day, your server is no longer just interacting
with a web browser.  Instead it's interfacing with desktop and mobile 
web browsers, multiple native applications, and maybe even being exposed
as an API to other developers.  Ripozo is designed to solve this problem.
It allows you to easily build Hypermedia/HATEOAS/REST APIs quickly and 
efficiently.

Full documentation
------------------

`ripozo documentation <https://ripozo.readthedocs.org/>`_

The ripozo ecosystem
--------------------

Currently, ripozo has integrations with Django, Flask, SQLAlchemy,
and Cassandra (via cqlengine).  The documentation links are provided
below.

======================================================================= ================================================================================
                          Frameworks                                                                     Databases
======================================================================= ================================================================================
`flask-ripozo <https://github.com/vertical-knowledge/flask-ripozo>`_     `ripozo-sqlalchemy <https://github.com/vertical-knowledge/ripozo-sqlalchemy>`_
`django-ripozo <https://github.com/vertical-knowledge/django-ripozo>`_   `ripozo-cassandra <https://github.com/vertical-knowledge/ripozo-cassandra>`_
======================================================================= ================================================================================

Built an extension for ripozo? Let us know and we'll add it in here!

Helpful links
-------------

- `flask-ripozo/ripozo-sqlalchemy tutorial <http://flask-ripozo.readthedocs.org/en/latest/flask_tutorial.html>`_
- `django-ripozo tutorial <http://django-ripozo.readthedocs.org/en/latest/tutorial/setup.html>`_

Why ripozo?
-----------

- Strong support for HATEOAS/Hypermedia
- Flexible (can be used with any web framework, database, or response protocol)
- Fast development (especially when using the extensions, such as flask-ripozo or django-ripozo)

Installation
------------

.. code-block:: bash

    pip install ripozo

Example
-------

.. code-block:: python

    from ripozo import apimethod, adapters, ResourceBase
    # import the dispatcher class for your preferred webframework

    class MyResource(ResourceBase):
        @apimethod(methods=['GET'])
        def say_hello(cls, request):
            return cls(properties=dict(hello='world'))

    # initialize the dispatcher for your framework
    # e.g. dispatcher = FlaskDispatcher(app)
    dispatcher.register_adapters(adapters.SirenAdapter, adapters.HalAdapter)
    dispatcher.register_resources(MyResource)

And just like that, you have an api that can return either Siren or Hal
formatted responses.  Pretty easy, right?

Versioning
==========

Prior to version 1.0.0 ripozo versioning follows `sentimental
versioning <http://sentimentalversioning.org/>`_.   Releases after 1.0.0 ollow
a standard *major.minor.patch* style.

- patch: forwards and backwards compatible
- minor: backwards compatible
- major: No guarantees

Contributing
============

Want to help out? We'd love it! Github will be the hub of development for ripozo.
If you have any issues, comments, or complaints post them there.  Additionally, we
are definitely accepting pull requests (hint: we almost always love more tests and
documentation).  We do have just a few requests:

* Every method, function, and class should have a thorough docstring
* There should be at least one unit test for each function and method
* Keep your pull requests to one issue. (Preferably open an issue on github first for record keeping)

.. _`ripozo-cassandra: <https://github.com/vertical-knowledge/ripozo-cassandra>`_

.. _`ripozo-sqlalchemy: <https://github.com/vertical-knowledge/ripozo-sqlalchemy>`_

.. _`django-ripozo: <https://github.com/vertical-knowledge/django-ripozo>`_

.. _`flask-ripozo: <https://github.com/vertical-knowledge/flask-ripozo>`_
