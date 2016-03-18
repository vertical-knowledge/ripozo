ripozo
======

.. image:: ./logos/ripozo-logo.png
    :target: http://ripozo.org
    :alt:

.. image:: https://travis-ci.org/vertical-knowledge/ripozo.svg?branch=master&style=flat
    :target: https://travis-ci.org/vertical-knowledge/ripozo
    :alt: test status

.. image:: https://coveralls.io/repos/vertical-knowledge/ripozo/badge.svg?branch=master&style=flat
    :target: https://coveralls.io/r/vertical-knowledge/ripozo?branch=master
    :alt: test coverage

.. image:: https://readthedocs.org/projects/ripozo/badge/?version=latest
    :target: https://ripozo.readthedocs.org/
    :alt: Documentation Status

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


Ripozo is a tool for building RESTful/HATEOAS/Hypermedia apis.  It provides
strong, simple, and fully qualified linking between resources, the ability to expose
available actions and necessary parameters on a resource, and exposing
multiple REST protocols (i.e. SIREN and HAL).  Finally, ripozo is highly extensible.
It is able to integrate with any web framework or database and you can easily roll out
your own REST protocols.

Why use ripozo?

- Strong support for inter-resource linking (HATEOAS/Hypermedia)
- Flexible (can be used with any web framework, database, or response protocol)
- Fast development (especially when using the extensions, such as flask-ripozo or django-ripozo)
- Ability to expose actions on resource from the web api (self-discoverability)

Examples
--------

You'll need to create a dispatcher using one of the dispatchers included
in the framework extensions.  You can find a list of framework extensions in
`The ripozo ecosystem`_ section.  If it's not there you can always roll out your own.

Minimal
^^^^^^^

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

Full CRUD+L
^^^^^^^^^^^

On the other hand, if you wanted a full CRUD+L (Create, Retrieve, Update, Delete, and List),
you could use one of the manager extensions (`django-ripozo`_, `ripozo-sqlalchemy`_, and `ripozo-cassandra`_ all
include ready to use base managers). There are slight differences
on creating Manager classes and instances in the different extensions but at a core they all follow this
format.

.. code-block:: python

    from ripozo import restmixins
    from fake_ripozo_extension import Manager
    from myapp.models import MyModel # An ORM model for example a sqlalchemy or Django model.

    class MyManager(Manager):
        fields = ('id', 'field1', 'field2',)
        model = MyModel

    class MyResource(restmixins.CRUDL):
        manager = MyManager()
        pks = ('id',)

    # Create your dispatcher and register the resource...

It is important to note that there are restmixins for each of
the individual CRUD+L (i.e. restmixins.Create, restmixins.Retrieve, etc.)
actions that can be mixed and matched to your pleasure.

Links
^^^^^

The coolest part of ripozo is the ability to easily create fully qualified links between
resources.

.. code-block:: python

    from ripozo import restmixins, Relationship

    class MyResource(restmixins.CRUDL):
        manager = MyManager()
        pks = ('id',)
        _relationships = [Relationship('related', relation='RelatedResource')]

    class RelatedResource(restmixins.CRUDL)
        manager = RelatedManager()
        pks = ('id',)

Now whenever you request MyResource you'll get a link pointing to
the related resource.


Documentation
-------------

`ripozo documentation <http://ripozo.readthedocs.org>`_

The ripozo ecosystem
^^^^^^^^^^^^^^^^^^^^

Currently, ripozo has integrations with Django, Flask, SQLAlchemy,
and Cassandra (via cqlengine).  The documentation links are provided
below.

===================   ===========================
   Frameworks             Databases
===================   ===========================
`flask-ripozo`_       `ripozo-sqlalchemy`_
`django-ripozo`_      `ripozo-cassandra`_
===================   ===========================

Built an extension for ripozo? Let us know and we'll add it in here!

Helpful links
^^^^^^^^^^^^^

- `flask-ripozo/ripozo-sqlalchemy tutorial <http://flask-ripozo.readthedocs.org/en/latest/flask_tutorial.html>`_
- `django-ripozo tutorial <http://django-ripozo.readthedocs.org/en/latest/tutorial/setup.html>`_

Installation
------------

.. code-block:: bash

    pip install ripozo


Versioning
----------

Prior to version 1.0.0 ripozo versioning follows `sentimental
versioning <http://sentimentalversioning.org/>`_.   Releases after 1.0.0 follow
a standard *major.minor.patch* style.

- patch: forwards and backwards compatible
- minor: backwards compatible
- major: No guarantees

Contributing
------------

Want to help out? We'd love it! Github will be the hub of development for ripozo.
If you have any issues, comments, or complaints post them there.  Additionally, we
are definitely accepting pull requests (hint: we almost always love more tests and
documentation).  We do have just a few requests:

* Every method, function, and class should have a thorough docstring
* There should be at least one unit test for each function and method
* Keep your pull requests to one issue. (Preferably open an issue on github first for record keeping)

Behind the name
---------------

Ripozo translates to  "rest" in Esperanto.  Esperanto was designed to be a universal language.  Anyone,
no matter their native language, can learn and use it easily.  Similarly, ripozo is intended
to be a universal ReST framework.  No matter your preference of database, web framework, or 
protocol, ripozo makes it easy to build.  

.. _ripozo-cassandra: https://github.com/vertical-knowledge/ripozo-cassandra

.. _ripozo-sqlalchemy: https://github.com/vertical-knowledge/ripozo-sqlalchemy

.. _django-ripozo: https://github.com/vertical-knowledge/django-ripozo

.. _flask-ripozo: https://github.com/vertical-knowledge/flask-ripozo
