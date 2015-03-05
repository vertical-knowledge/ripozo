Tutorial Part 1: Resources
==========================

Resources are the core of ripozo.  These define
what can be accessed and the actions you can
perform on those resources.  They are designed to be
common across all ripozo integrations.  In other words,
if they are designed correctly, a resource should be
able to be plugged into different web frameworks and managers
should be able to be plugged in and out.

Minimal Application
-------------------

.. code-block:: python

   from ripozo import ResourceBase, apimethod


   class MyResource(ResourceBase):
       _resource_name = 'my_resource'

       @apimethod(methods=['GET'])
       def hello_world(cls, request):
           return cls(properties=dict(hello='world'))