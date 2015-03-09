Tutorial Part 3: Managers
=========================

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
be on the resource classes.

Creating a manager extensions
-----------------------------

See :doc:`../extending/managers.rst` for more details on extending ripozo

