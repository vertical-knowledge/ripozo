Managers
========

Managers are the persistence abstraction layer in ripozo.
They are responsible for all session to session persistence in
a ripozo based application.  Typically, we can assume that the persistence
layer is a database.  However, the actual method of persistence is
irrelevant to ripozo.  There are ripozo extensions that are specifically
for certain database types.  At the most basic level, all ripozo ManagerBase
subclasses must implement basic CRUD+L.  That is they must implement a create,
retrieve, update, delete an retrieve_list methods.

Managers in ripozo are not required and are more intended as a way to create
a common interface for database interactions.  Additionally, they are intended,
to abstract away the database since individual database interactions should not
be on the resource classes.  The one caveat is that the restmixins will not
work without a manager defined.

Creating a manager extensions
-----------------------------

Manager extensions in ripozo can be somewhat tricky to
implement correctly.  Fortunately, it only needs to be
done once (and hopefully shared in the community).

There is only one absolutely critical piece that needs
to be implements for a manager to minimally work. The get_field_type
method helps the translation and validation work.  If not implemented,
your manager will not work in any case.  This method determines what
the python type is for the specified field.

*note* get_field_type is a classmethod.  That means you need to decorate
it with the builtin ``@classmethod`` decorator.

.. automethod:: ripozo.manager_base.BaseManager.get_field_type

Additionally, there are 5 basic CRUD+L operations.  Not all
of them need to be implemented (with some databases it may not
make sense).  However, the method should still be overridden
and a ``NotImplementedError`` exception should be raised if
it is called.  Also, keep in mind that if any methods are
not implemented then at least some of the restmixins will
not be available.

.. automethod:: ripozo.manager_base.BaseManager.create


.. automethod:: ripozo.manager_base.BaseManager.retrieve


.. automethod:: ripozo.manager_base.BaseManager.retrieve_list


.. automethod:: ripozo.manager_base.BaseManager.update


.. automethod:: ripozo.manager_base.BaseManager.delete



Base Manager API
----------------

.. autoclass:: ripozo.manager_base.BaseManager
    :members:
