Managers
========

The first step in setting up our RESTful application
is to define our managers.  Managers are responsible
for maintaining state in the application.  They are
the common interface for interacting with databases.

Defining managers is actually very simple:

.. code-block:: python

    from ripozo_sqlalchemy import AlchemyManager

    # This is the most basic session handler.
    # It simply passes the db.session object and
    # lets Flask-SQLAlchemy handle the rest.
    session_handler = SessionHandler(db.session)

    class TaskBoardManager(AlchemyManager):
        _fields = ('id', 'title', 'tasks.id',)
        _list_fields = ('id', 'title',)
        _update_fields = ('title',)
        model = TaskBoard
        paginate_by = 10

    class TaskManager(AlchemyManager):
        _fields = ('id', 'task_board_id', 'title', 'description', 'completed',)
        model = Task
        paginate_by = 20

And that's it.  This provided a common interface for
creating, updating, deleting, and retrieving both the
TaskBoard and Task.  These allow us to quickly implement
the common CRUD+L actions using the builtin Rest mixins.