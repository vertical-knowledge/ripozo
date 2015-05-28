Tutorial Part 4: Dispatchers
============================

Dispatchers are responsible for translating incoming requests
and dispatching them to the appropriate resources.  They then
take the response from the ResourceBase subclass and uses to appropriate
adapter to create a response.  Dispatchers are responsible for coupling ripozo
with a web framework.  As such, the dispatcher is not fully implemented in
ripozo.  Rather there is an abstract base class that must be implemented
for the specific framework that is being used.

Example
-------

When using a ripozo implementation for your preferred framework, registering
the resource classes is very easy.

.. code-block:: python

    # Import your resource classes
    from my_resources import MyResource, MyOtherResource

    # Import the adapters that you want to use
    from ripozo.dispatch.adapters import SirenAdapter, HalAdapter

    # Initialize your Dispatcher (this will be different for
    # different web frameworks.  Please look at the specific documentation
    # for that framework.
    # For example, in flask-ripozo it would be
    # app = Flask(app)
    # dispatcher = FlaskDispatcher(app)

    # register your adapters, the first adapter is the default adapter
    dispatcher.register_adapters(SirenAdapter, HalAdapter)

    # Register your resource classes
    dispatcher.register_resources(MyResource, MyOtherResource)

I wasn't lying, it's pretty basic.

Implementing a Dispatcher
-------------------------

If you're interested in building a dispatcher for your python web framework of
choice please see the :doc:`../extending/dispatchers.rst` for more information
on extending ripozo.

:doc:`tutorial_part_5.rst`
