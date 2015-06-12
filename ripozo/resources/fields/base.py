from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException
from ripozo.resources.constants import input_categories
from ripozo.exceptions import RestException

import six


class BaseField(object):
    """
    The BaseField class is simply an abstract base class
    that defines the necessary methods for casting and
    validating a field.
    """
    field_type = object

    def __init__(self, name, required=False, maximum=None,
                 minimum=None, arg_type=None, error_message=None):
        self.name = name
        self.required = required
        self.maximum = maximum
        self.minimum = minimum
        self.arg_type = arg_type
        self.error_message = error_message

    def translate(self, obj, skip_required=False, validate=False):
        """
        A shortcut method to _translate and _validate the object
        that is being passed in.  It returns this object
        or raises a ValueError.

        :param object obj:
        :return: The translated and validated object
        :rtype: object
        :raises: ripozo.exceptions.ValidationsException
        :raises: ripozo.exceptions.TranslationException
        """
        obj = self._translate(obj, skip_required=skip_required)
        if validate:
            obj = self._validate(obj, skip_required=skip_required)
        return obj

    def _translate(self, obj, skip_required=False):
        """
        This method is responsible for translating an input
        string or object.

        :param object obj: The input from the request
            that is being translated
        :param bool skip_required: This is being ignored for now
        :return: The object in the appropriate form
        :rtype: object
        :raises: ripozo.exceptions.TranslationException
        """
        if isinstance(obj, (list, set)):
            if len(obj) > 0:
                return obj[0]
            else:
                return None
        return obj

    def _validate(self, obj, skip_required=False):
        """
        An object to be validated

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
        if self.required and obj is None and skip_required is False:
            raise ValidationException(self.error_message or 'The field "{0}" is required '
                                                            'and cannot be None'.format(self.name))
        obj = self._validate_type(obj)
        return obj

    def _skip_validation(self, obj):
        """
        Deteremines whether validation should be skipped because
        the input is None and the field is not required.

        :param object obj:
        :return: A boolean indicating whether validation should
            be skipped
        :rtype: bool
        """
        if obj is None and not self.required:
            return True
        return False

    def _validate_size(self, obj, obj_size, msg=None):
        """
        Validates the size of the object.

        :param Sized obj_size: The size of the object.  This must be an object
            that is comparable, i.e. it must be comparable via  ">" and "<"
            operators
        :param msg: The message to display if the object fails validation
        :type msg: unicode
        :returns: The validated object
        :rtype: object
        :raises: ValidationException
        """
        if self.minimum and obj_size < self.minimum:
            if not msg:
                msg = ('The input was too small for the field {2}: '
                       '{0} < {1}'.format(obj_size, self.minimum, self.name))
            raise ValidationException(self.error_message or msg)
        if self.maximum and obj_size > self.maximum:
            if not msg:
                msg = ('The input was too large for the field {2}: '
                       '{0} > {1}'.format(obj_size, self.maximum, self.name))
            raise ValidationException(self.error_message or msg)
        return obj

    def _validate_type(self, obj, msg=None):
        """
        Validates that is object matches the classes field_type

        :param object obj:
        :return: The validated object
        :rtype: object
        """
        if obj is None and not self.required:
            return obj
        if obj is not None and isinstance(obj, self.field_type):
            return obj
        if msg is None:
            msg = "obj is not a valid type for field {0}. A type of {1} is required.".format(self.name, self.field_type)
        raise ValidationException(self.error_message or msg)


def translate_fields(request, fields=None, skip_required=False, validate=False):
    """
    Performs the specified action on the field.  The action can be a string of
     either _translate, _validate, or translate.

    :param RequestContainer request: The request that you are attempting to
        translate from.
    :param list fields: The list of BaseField instances that are supposed
        to be validated.  Only items in this list will be translated
        and validated
    :param bool skip_required: A flag that indicates the required fields
        are not required.  This is helpful for updates where fields are not
        usually required.
    :param bool validate: A flag that indicates whether the field validations
        should be run.  If not, it will just translate the fields.
    :return: Returns the translated url_params, query_args and body_args
    :rtype: tuple
    :raises: RestException
    :raises: ValidationException
    :raises: TranslationException
    """
    updated_url_params = request.url_params
    updated_query_args = request.query_args
    updated_body_args = request.body_args
    fields = fields or []
    for field in fields:
        field_name_in_request = field.name in request
        if not field_name_in_request and skip_required:
            continue
        field_value = field.translate(request.get(field.name, None, location=field.arg_type),
                                      skip_required=skip_required, validate=validate)
        if field_name_in_request:
            request.set(field.name, field_value, location=field.arg_type)

    return updated_url_params, updated_query_args, updated_body_args
