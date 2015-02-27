from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Tim Martin'


class RestException(Exception):
    """
    The base exception for any of the package
    specific exceptions
    """
    pass


class NoResourceNameDeclaredException(RestException):
    """
    An exception raised when neither the _resource_name
    or the _manager attributes are set on a ResourceBase
    subclass.  When this happens it is impossible for the
    ResourceBase subclass to determine what to call the
    resource it is handling
    """
    pass


class BaseRestEndpointAlreadyExists(RestException):
    """
    This exception is raised when the ResourceBaseMetaClass
    finds an endpoint has already been registered for the application
    """
    pass


class ManagerException(RestException):
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


class FieldException(RestException, ValueError):
    """
    An exception specifically for Field errors.  Specifically,
    when validation or casting fail.
    """
    pass


class ValidationException(FieldException):
    """
    An exception for when validation fails on a field.
    """
    pass


class TranslationException(ValidationException):
    """
    An exception that is raised when casting fails on
    a field.
    """
    pass


class DispatchException(RestException):
    """
    An exception for when something is wrong with the Dispatcher
    """
    pass


class AdapterFormatAlreadyRegisteredException(DispatchException):
    """
    An exception that is raised when an adapter format has already
    been register with the adapter instance.  This is done
    to prevent accidental overrides of format types.
    """
    pass