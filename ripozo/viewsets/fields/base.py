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

    def __init__(self, name, default=None, required=False, maximum=None,
                 minimum=None, arg_type=input_categories.QUERY_ARGS):
        self.name = name
        self.required = required
        self.maximum = maximum
        self.minimum = minimum
        self.arg_type = arg_type
        self.default = default

    def translate_and_validate(self, obj):
        """
        A shortcut method to translate and validate the object
        that is being passed in.  It returns this object
        or raises a ValueError.

        :param object obj:
        :return: The translated and validated object
        :rtype: object
        :raises: ripozo.exceptions.ValidationsException
        :raises: ripozo.exceptions.TranslationException
        """
        obj = self.translate(obj)
        return self.validate(obj)

    def translate(self, obj):
        """
        This method is responsible for translating an input
        string or object.

        :param object obj: The input from the request
            that is being translated
        :return: The object in the appropriate form
        :rtype: object
        :raises: ripozo.exceptions.TranslationException
        """
        if obj is None:
            return self.default
        return obj

    def validate(self, obj):
        """
        An object to be validated

        :param object obj:
        :return: The same exact object simple validated.
        :rtype: object
        :raises: ripozo.exceptions.ValidationException
        """
        if self.required and obj is None:
            raise ValidationException('The object is required and cannot be None')
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
            raise ValidationException(msg)
        if self.maximum and obj_size > self.maximum:
            if not msg:
                msg = ('The input was too large for the field {2}: '
                       '{0} > {1}'.format(obj_size, self.maximum, self.name))
            raise ValidationException(msg)
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
        raise ValidationException(msg)


def translate_and_validate_fields(url_params, query_args, body_args, fields=None):
    """
    Translates and validates the supplied parameters against the
    list of BaseField instances provided

    :param dict url_params: The url parameters.  Typically this is going
        to be things like primary keys and such
    :param dict query_args: The query args.  Typically these are going to be
        filters on lists and such
    :param dict body_args: The arguments in the body.  This may be for
        updates and creations
    :param list fields: The list of BaseField instances that are supposed
        to be validated.  Only items in this list will be translated
        and validated
    :return: Returns the translated url_params, query_args and body_args
    :rtype: tuple
    :raises: RestException
    :raises: ValidationException
    :raises: TranslationException
    """
    return _translate_or_validate_helper(url_params, query_args, body_args,
                                         fields=fields, action='translate_and_validate')


def validate_fields(url_params, query_args, body_args, fields=None):
    """
    Validates the supplied parameters against the
    list of BaseField instances provided

    :param dict url_params: The url parameters.  Typically this is going
        to be things like primary keys and such
    :param dict query_args: The query args.  Typically these are going to be
        filters on lists and such
    :param dict body_args: The arguments in the body.  This may be for
        updates and creations
    :param list fields: The list of BaseField instances that are supposed
        to be validated.  Only items in this list will be translated
        and validated
    :return: Returns the translated url_params, query_args and body_args
    :rtype: tuple
    :raises: RestException
    :raises: ValidationException
    :raises: TranslationException
    """
    return _translate_or_validate_helper(url_params, query_args, body_args,
                                         fields=fields, action='validate')


def translate_fields(url_params, query_args, body_args, fields=None):
    """
    Translates and validates the supplied parameters against the
    list of BaseField instances provided

    :param dict url_params: The url parameters.  Typically this is going
        to be things like primary keys and such
    :param dict query_args: The query args.  Typically these are going to be
        filters on lists and such
    :param dict body_args: The arguments in the body.  This may be for
        updates and creations
    :param list fields: The list of BaseField instances that are supposed
        to be validated.  Only items in this list will be translated
        and validated
    :return: Returns the translated url_params, query_args and body_args
    :rtype: tuple
    :raises: RestException
    :raises: ValidationException
    :raises: TranslationException
    """
    return _translate_or_validate_helper(url_params, query_args, body_args, fields=fields, action='translate')


def _translate_or_validate_helper(url_params, query_args, body_args, fields=None, action=None):
    """
    Performs the specified action on the field.  The action can be a string of
     either translate, validate, or translate_and_validate.

    :param dict url_params: The url parameters.  Typically this is going
        to be things like primary keys and such
    :param dict query_args: The query args.  Typically these are going to be
        filters on lists and such
    :param dict body_args: The arguments in the body.  This may be for
        updates and creations
    :param list fields: The list of BaseField instances that are supposed
        to be validated.  Only items in this list will be translated
        and validated
    :param unicode action: The unicode name of the method to call on all of the
        fields.  It is found via getattr.
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
    action_name = action
    for field in fields:
        action = getattr(field, action_name)
        # Translate and validate the inputs
        if field.arg_type == input_categories.URL_PARAMS:
            updated_url_params[field.name] = action(url_params.get(field.name, None))
        elif field.arg_type == input_categories.BODY_ARGS:
            updated_body_args[field.name] = action(body_args.get(field.name, None))
        elif field.arg_type == input_categories.QUERY_ARGS:
            updated_query_args[field.name] = action(query_args.get(field.name, None))
        else:
            raise RestException('Invalid arg_type, {0}, on Field {1}'.format(field.arg_type, field.name))
    return updated_url_params, updated_query_args, updated_body_args