from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import ABCMeta


class AdapterMeta(ABCMeta):
    """
    The meta class that is responsible for registering adapters.
    All adapters should be allowed by default hence the meta-class.

    :param dict formats: A dictionary with the format names/types as
        the key and the responsible klass for that format type as
        the value.
    """
    formats = None

    def __new__(mcs, name, bases, attrs):
        """
        Registers the format to the dispatch

        :param unicode name: The name of the new class
        :param tuple bases: A tuple of the bases of the class
            that is being created
        :param dict attrs: A dictionary of the attributes on
            the new class
        :return: The klass that is now registered
        :rtype: type
        """
        klass = super(AdapterMeta, mcs).__new__(mcs, name, bases, attrs)
        if not mcs.formats:
            mcs.formats = {}
        if not attrs.get('__abstract__', False):
            for f in klass.formats:
                mcs.formats[f] = klass
        return klass
