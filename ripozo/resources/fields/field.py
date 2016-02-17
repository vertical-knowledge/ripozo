from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

from ripozo.resources.fields.validations import basic_validation, translate_iterable_to_single


@six.add_metaclass(abc.ABCMeta)
class IField(object):
    """
    The BaseField class is simply an abstract base class
    that defines the necessary methods for casting and
    validating a field.
    """
    field_type = object

    def __init__(self, name, required=False, error_message=None, arg_type=None):
        self.name = name
        self.required = required
        self.error_message = error_message
        self.arg_type = arg_type

    def translate(self, obj, skip_required=False, validate=False):
        """
        A shortcut method to _translate and _validate the object
        that is being passed in.  It returns this object
        or raises a ValueError.

        :param object obj: The object to translate and validate
            if validate is ``True``
        :param bool skip_required: A boolean indicating whether
            the required validation should be skipped
        :param bool validate: If ``True`` the validations
             will be run.  Otherwise the field will not be
             validated.
        :return: The translated and validated object
        :rtype: object
        :raises: ripozo.exceptions.ValidationsException
        :raises: ripozo.exceptions.TranslationException
        """
        if obj is not None:  # None objects should be handled by validation
            obj = self._translate(obj, skip_required=skip_required)
        if validate:
            obj = self._validate(obj, skip_required=skip_required)
        return obj

    @abc.abstractmethod
    def _translate(self, obj, skip_required=False):
        raise NotImplementedError

    @abc.abstractmethod
    def _validate(self, obj, skip_required=False):
        raise NotImplementedError


class Field(IField):
    """
    The BaseField class is simply an abstract base class
    that defines the necessary methods for casting and
    validating a field.
    """
    field_type = object

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
        return translate_iterable_to_single(obj)

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
        return basic_validation(self, obj, skip_required=skip_required)
