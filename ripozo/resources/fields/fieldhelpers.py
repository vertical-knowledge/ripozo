from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException


def validate_type(field, field_type, obj, msg=None):
    """
    Validates that is object matches the classes field_type.

    :param ripozo.resource.fields.base.BaseField field: The field
        that specifies the validation
    :param type field_type: The type that the object must be
    :param object obj: The object that is being validated
    :param unicode msg: The error message to use if field.error_message
        is ``None``.
    :return: The validated object
    :rtype: object
    """
    if isinstance(obj, field_type):
        return obj
    if msg is None:
        msg = ("obj is not a valid type for field {0}. A type of"
               " {1} is required.".format(field.name, field_type))
    raise ValidationException(field.error_message or msg)


def validate_size(field, obj, obj_size, minimum=None, maximum=None, msg=None):
    """
    Validates the size of the object.

    :param ripozo.resources.fields.base.BaseField field: The field that
        is being validated
    :param object obj: The object that needs to match the specifications
        of the field
    :param Sized obj_size: The size of the object.  This must be an object
        that is comparable, i.e. it must be comparable via  ">" and "<"
        operators
    :param Sized minimum: The minimum value for the object
    :param Sized maximum: The maximum value for the object
    :param unicode msg: The message to display if the object fails validation
    :returns: The validated object
    :rtype: object
    :raises: ValidationException
    """
    if minimum and obj_size < minimum:
        if not msg:
            msg = ('The input was too small for the field {2}: '
                   '{0} < {1}'.format(obj_size, minimum, field.name))
        raise ValidationException(field.error_message or msg)
    if maximum and obj_size > maximum:
        if not msg:
            msg = ('The input was too large for the field {2}: '
                   '{0} > {1}'.format(obj_size, maximum, field.name))
        raise ValidationException(field.error_message or msg)
    return obj

