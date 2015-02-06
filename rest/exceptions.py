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


class ManagerException(RestExceptions):
    """
    A base exception for when the manager has an exception specific
    to it. For example, not finding a model.
    """
    pass


class NotFoundException(ManagerException):
    """
    This exception is raised when the manager can't
    find a model that was requested.
    """
    pass