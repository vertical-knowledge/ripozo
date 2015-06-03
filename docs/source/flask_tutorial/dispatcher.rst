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

We now have a functioning RESTful api that serves both.
To start up this application, we just need to run:

.. code-block:: python

    app.run()
