from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Tim Martin'


class RestExceptions(Exception):
    """
    The base exception for any of the package
    specific exceptions
    """
    pass


class BaseRestEndpointAlreadyExists(RestExceptions):
    """
    This exception is raised when the ResourceBaseMetaClass
    finds an endpoint has already been registered for the application
    """
    pass