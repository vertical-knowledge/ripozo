"""
Contains the exceptions
that ripozo explicitly uses.
"""
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
    def __init__(self, message=None, status_code=500, *args, **kwargs):
        super(RestException, self).__init__(message, *args, **kwargs)
        self.status_code = status_code


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
    def __init__(self, message, status_code=404, *args, **kwargs):
        super(NotFoundException, self).__init__(message, status_code=status_code, *args, **kwargs)


class FieldException(RestException, ValueError):
    """
    An exception specifically for Field errors.  Specifically,
    when validation or casting fail.
    """
    def __init__(self, message, status_code=400, *args, **kwargs):
        super(FieldException, self).__init__(message, status_code=status_code, *args, **kwargs)


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


class JSONAPIFormatException(RestException):
    """
    This exception is raised when a request is not
    properly formatted according to the
    `JSON API specification <http://jsonapi.org/format/#crud>`_
    """
    def __init__(self, message, status_code=400, *args, **kwargs):
        super(JSONAPIFormatException, self).__init__(message, status_code=status_code, *args, **kwargs)


class UnreadableBodyException(RestException):
    """
    Occurs when the request body cannot be parsed appropriately
    either because the character set was not correct or the format
    was incorrect (i.e. form-encoded when the content-type is
    application/json)
    """
    def __init__(self, message, status_code=400, *args, **kwargs):
        super(UnreadableBodyException, self).__init__(message, status_code=status_code, *args, **kwargs)


class UnsupportedMediaTypeException(RestException):
    """
    Raised when the server sends a request with a Content-Type
    that the server cannot handle.  E.g. if the client sends a request
    with ``"Content-Type: application/something-not-supported"`` and
    the server does not have an adapter that supports
    ``"application/something-not-supported"``

    The status code is ``415`` if this is propagated to the client.
    """

    def __init__(self, message, status_code=415, *args, **kwargs):
        super(UnsupportedMediaTypeException, self).__init__(message, status_code=status_code, *args, **kwargs)
