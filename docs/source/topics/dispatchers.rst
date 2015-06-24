Dispatchers
===========

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

So you've just discovered the next great python web
framework.  Unfortunately, nobody has developed a ripozo
dispatcher implementation for it yet.  Don't despair!  Implementing
a ripozo dispatcher is theoretically quite simple.  There is only
one method and one property you need to implement.

The first is the base_url property.  This is base_url
that is used when constructing urls.  For example, it might
include the the host, port and base path (e.g. ``'http://localhost:5000/api'``).
If you absolutely need to make it a method, you will need to overrided the dispatch
method as well, since it expects it to be a property.

.. automethod:: ripozo.dispatch_base.DispatchBase.base_url


The second piece you'll need to implement is the register_route
method.  This is the method that is responsible for taking
an individual route and relaying it to the webframework.

.. automethod:: ripozo.dispatch_base.DispatcherBase.register_route


For a real life example of implementing a dispatcher check out the
`flask dispatcher.<https://github.com/vertical-knowledge/flask-ripozo/blob/master/flask_ripozo/dispatcher.py>`_


Dispatcher API
--------------

.. automodule:: ripozo.dispatch_base.DispatcherBase
    :members:
