Adapters
========

Adapters are responsible for transforming a
Resource instance into a request body string.
For example, in the SirenAdapter, they would
put the properties in a dictionary called "properties",
the related resource in a list called "entities",
and so on and so forth.  All adapters instantiation
requires at least a resource instance.

Finally, adapters are independent of web framework
and database/managers used.  This means that you can
completely reuse adapters across all of your applications.

Building your own adapter
-------------------------

At some point or another, you will probably
want to roll out your own adapter.  Maybe you
are using a front-end framework that is expecting
a specific format or maybe you're porting over
from django-rest-framework and don't want to
have to change your front-end.  Either way, you
want some flexibility in how the resource gets formatted.

For an example of a basic adapter check out the built in
`JSON adapter. <https://github.com/vertical-knowledge/ripozo/blob/master/ripozo/adapters/boring_json.py>`_

Required pieces
^^^^^^^^^^^^^^^

.. py:attribute:: formats

    A tuple or list of available formats in unicode/str form.
    These are the formats that are used to match the requests
    accept-types with the appropriate adapter.


.. autoattribute:: ripozo.adapters.base.AdapterBase.formatted_body


.. autoattribute:: ripozo.adapters.base.AdapterBase.extra_headers


Optional pieces
^^^^^^^^^^^^^^^

These methods do not have to be implemented in the subclass
but in some cases it may make more sense.

.. automethod:: ripozo.adapters.base.AdapterBase.format_exception


Adapters API
------------

Built in adapters
^^^^^^^^^^^^^^^^^

.. autoclass:: ripozo.adapters.siren.SirenAdapter
    :members:

.. autoclass:: ripozo.adapters.hal.HalAdapter
    :members:

.. autoclass:: ripozo.adapters.basic_json.BasicJSONAdapter
    :members:

Base Adapter
^^^^^^^^^^^^

.. autoclass:: ripozo.adapters.base.AdapterBase
    :members:
