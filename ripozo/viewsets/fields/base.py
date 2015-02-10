from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException

import six


@six.python_2_unicode_compatible
class BaseField(object):
    """
    The BaseField class is simply an abstract base class
    that defines the necessary methods for casting and
    validating a field.
    """

    def __init__(self, name, required=False):
        self.name = name
        self.required = required

    def __str__(self):
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
        return obj