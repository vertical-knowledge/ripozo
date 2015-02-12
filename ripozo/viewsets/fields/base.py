from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException
from ripozo.viewsets.constants.input_categories import QUERY_ARGS

import six


@six.python_2_unicode_compatible
class BaseField(object):
    """
    The BaseField class is simply an abstract base class
    that defines the necessary methods for casting and
    validating a field.
    """
    field_type = object

    def __init__(self, name, default=None, required=False, maximum=None, minimum=None, arg_type=QUERY_ARGS):
        self.name = name
        self.required = required
        self.maximum = maximum
        self.minimum = minimum
        self.arg_type = arg_type
        self.default = default

    def __str__(self):
        """
        :return: The name of the field
        :rtype: unicode
        """
        return self.name

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
        if not obj:
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
        if obj and isinstance(obj, self.field_type):
            return obj
        if msg is None:
            msg = "obj is not a valid type for field {0}. A type of {1} is required.".format(self.name, self.field_type)
        raise ValidationException(msg)