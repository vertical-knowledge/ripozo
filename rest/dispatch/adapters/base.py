from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from abc import abstractmethod, abstractproperty
from rest.dispatch.adapters.contructor import AdapterMeta
import six


# TODO docs
@six.add_metaclass(AdapterMeta)
class AdapterBase(object):
    __abstract__ = True

    def __init__(self, resource):
        """

        :param resource:
        :type resource: rest.viewsets.resource_base.ResourceBase
        """
        self.resource = resource

    @abstractmethod
    def get_formatted_body(self):
        """

        :return:
        :rtype: unicode
        """
        pass

    @abstractproperty
    def extra_headers(self):
        """

        :return:
        :rtype: list
        """
        pass
