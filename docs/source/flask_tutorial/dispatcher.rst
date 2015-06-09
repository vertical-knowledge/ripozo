Dispatchers
===========

Dispatchers are responsible for registering
our resources with the flask application.
This allows us to actually call our endpoints.

.. code-block:: python

    from flask_ripozo import FlaskDispatcher
    from ripozo import adapters

    dispatcher = FlaskDispatcher(app, url_prefix='/api')
    dispatcher.register_resources(TaskBoardResourceList, TaskBoardResource, TaskResource)
    dispatcher.register_adapters(adapters.SirenAdapter, adapters.HalAdapter)

We now have a functioning RESTful api that serves both
Siren and HAL protocls.

To start up this application, we just need to run:

.. code-block:: python

    app.run()

Using the api
=============

We'll be using pypermedia to access the
api.  It makes it extremely easy to use
a SIREN based protocol.  You could use
HAL protocol if you preferred by prepending
that to your accept-types.

.. code-block:: bash

    pip install pypermedia

First we'll create a task board

.. code-block:: python


    >>> siren_client = HypermediaClient.connect('http://127.0.0.1:5000/api/taskboard/', request_factory=requests.Request)
    >>> task_board_list = siren_client.retrieve_list()
    >>> created = task_board_list.create(title='My First Board')
    >>> retrieve = created.retrieve()
    >>> print(created.title)
    'My First Board'
    >>> print(created.id)
    5

Now we can update the board's title.

.. code-block:: python

    >>> updated = retrieve.update(title='My Updated Board')
    >>> print(updated.title)
    'My Updated Board'

Of course we can't have a task board without any tasks!

.. code-block:: python
    >>> new_task = updated.add_task(title='My first task', description='I need to do something')
    >>> print(new_task.title)
    'My first task'
    >>> print(new_task.description)
    'I need to do something'
    >>> print(new_task.completed)
    False

We can now get this task from the task board itself.

.. code-block:: python

    >>> task_board = retrieve.retrieve()
    >>> task = next(task_board.get_entities('tasks'))
    >>> print(task.description)
    'I need to do something'
    >>> print(task.completed)
    False

Well I guess we did something.  We'll update the task.

.. code-block:: python

    >>> task = task.update(completed=True)
    >>> print(task.completed)
    True

And we can get the board this task belonds to by getting the task_board entity

.. code-block:: python

    >>> parent_board = next(task.get_entities('task_board'))
    >>> print(parent_board.title)
    My Updated Board

That task is dumb.  Let's delete it.

.. code-block:: python

    >>> deleted = task.delete()
    >>> original_task = task.retrieve()
    >>> print(original_task)
    None
