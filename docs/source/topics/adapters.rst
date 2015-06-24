Adapters
========

Adapters are responsible for transforming a
Resource instance into a request body string.
For example, in the SirenAdapter, they would
put the properties in a dictionary called "properties",
the related resource in a list called "entities",
and so on and so forth.  All adapters instantiation
requires at least a resource instance.

Building your own adapter
-------------------------


Adapters API
------------

Built in adapters
^^^^^^^^^^^^^^^^^

.. autoclass:: ripozo.adapters.siren.SirenAdapter
    :members:

.. autoclass:: ripozo.adapters.hal.HalAdapter
    :members:

.. autoclass:: ripozo.adapters.boring_json.BoringJSON
    :members:

Base Adapter
^^^^^^^^^^^^

.. automodule:: ripozo.adapters.base.BaseAdapter
    :members:
