from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException


def translate_iterable_to_single(obj):
    """
    Retrieves the first item from the list if the object
    is a list or set.  Otherwise, it simply returns the object.

    :param object obj:
    :return: The original object if it was not a list
        or set, otherwise the first item in the list or set
    :rtype: object
    """
    if isinstance(obj, (list, set)):
        return obj[0] if obj else None
    return obj


def validate_required(field, obj, skip_required=False):
    """
    Validates if the item is not None or not required

    :param object obj: The object to validate
    :return: The original object
    :rtype: object
    :raises: ValidationException
    """
    if field.required and obj is None and skip_required is False:
        raise ValidationException(field.error_message or 'The field "{0}" is required '
                                                         'and cannot be None'.format(field.name))
    return obj


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

    :param ripozo.resources.fields.field.IField field: The field that
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


def validate_regex(field, obj, regex=None):
    """
    Validates a string against a regular expression.
    The regular expression must be compiled.  This
    validation is skipped if the regex is None

    :param ripozo.resources.fields.field.IField field:
    :param _sre.SRE_Pattern regex: A compiled regular expression that must
        match at least once.
    :param unicode obj: The string to validate
    :return: The original object
    :rtype: object
    """
    if regex and not regex.match(obj):
        msg = field.error_message or ('The input string for the field '
                                      '{2} did not match the'
                                      ' required regex: {0} != {1}'
                                      ''.format(obj, regex.pattern, field.name))
        raise ValidationException(msg)
    return obj


def basic_validation(field, obj, skip_required=False):
    """
    Validates if the object exists for a required field
    and if the object is of the correct type.

    :param ripozo.resources.fields.field.IField field: The field object
        that contains the necessary parameters for validating a field.
    :param object obj:
    :param bool skip_required: If this is set to True
        then the required statement will be skipped
        regardless of whether the field is actually
        required or not.  This is useful for circumstances
        where you want validations to run and the field is
        normally required but not in this case.  See the
        restmixins.Update for an example.
    :return: The same exact object simple validated.
    :rtype: object
    :raises: ripozo.exceptions.ValidationException
    """
    obj = validate_required(field, obj, skip_required=skip_required)
    if obj is None:
        return obj
    obj = validate_type(field, field.field_type, obj)
    return obj
