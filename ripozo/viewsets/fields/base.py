from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException
from ripozo.viewsets.constants import input_categories
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
                 minimum=None, arg_type=input_categories.BODY_ARGS,
                 error_message=None):
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


def translate_fields(url_params, query_args, body_args, fields=None, skip_required=False, validate=False):
    """
    Performs the specified action on the field.  The action can be a string of
     either _translate, _validate, or translate.

    :param dict url_params: The url parameters.  Typically this is going
        to be things like primary keys and such
    :param dict query_args: The query args.  Typically these are going to be
        filters on lists and such
    :param dict body_args: The arguments in the body.  This may be for
        updates and creations
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
    updated_url_params = url_params.copy()
    updated_query_args = query_args.copy()
    updated_body_args = body_args.copy()
    fields = fields or []
    for field in fields:
        if field.arg_type == input_categories.URL_PARAMS:
            args = updated_url_params
        elif field.arg_type == input_categories.QUERY_ARGS:
            args = updated_query_args
        elif field.arg_type == input_categories.BODY_ARGS:
            args = updated_body_args
        else:
            raise RestException('Invalid arg_type, {0}, on Field {1}'.format(field.arg_type, field.name))

        if field.name not in args and skip_required:
            continue
        field_value = field.translate(args.get(field.name, None),
                                      skip_required=skip_required, validate=validate)
        if field.name in args:
            args[field.name] = field_value

    return updated_url_params, updated_query_args, updated_body_args