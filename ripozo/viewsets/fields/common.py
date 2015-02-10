from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException, TranslationException
from ripozo.viewsets.fields.base import BaseField

import six


class StringField(BaseField):
    """
    Used for casting and validating string fields.
    """

    def __init__(self, name, max_length=None, min_length=None, regex=None, required=False):
        """
        A field class for validating string inputs.

        :param int max_length: The maximum length of the string
        :param int min_length: The minimum legnth of the string
        :param _sre.SRE_Pattern regex: A compiled regular expression that must
            match at least once.
        """
        super(StringField, self).__init__(name, required=required)
        self.max_length = max_length
        self.min_length = min_length
        self.regex = regex

    def translate(self, obj):
        # TODO
        obj = super(StringField, self).translate(obj)
        try:
            return six.text_type(obj)
        except ValueError:
            raise TranslationException('obj is not a valid unicode string: {0}'.format(obj))

    def validate(self, obj):
        # TODO
        obj = super(StringField, self).validate(obj)
        if not isinstance(obj, six.string_types):
            raise ValidationException('The object validated is not a string: {0}'.format(obj))
        if self.max_length and len(obj) > self.max_length:
            raise ValidationException('The input string was too long: {0} > {1}'.format(len(obj), self.max_length))
        if self.min_length and len(obj) < self.min_length:
            raise ValidationException('The input string was too short '
                                      'for validation: {0} < {1}'.format(len(obj), self.min_length))
        if not self.regex.match(obj):
            raise ValidationException('The input string did not match the'
                                      ' required regex: {0} != {1}'.format(obj, self.regex))

        # passed validation
        return obj


class IntegerField(BaseField):
    # TODO
    def __init__(self, name, maximum=None, minimum=None, required=False):
        super(IntegerField, self).__init__(name, required=required)
        self.maximum = maximum
        self.minimum = minimum

    def translate(self, obj):
        obj = super(IntegerField, self).translate(obj)
        try:
            return int(obj)
        except ValueError:
            raise TranslationException('Not a valid integer type: {0}'.format(obj))

    def validate(self, obj):
        obj = super(IntegerField, self).validate(obj)
        obj = self._type_helper(obj)
        if self.maximum and obj > self.maximum:
            raise ValidationException('The object is larger than the required'
                                      ' maximum: {0} > {1}'.format(obj, self.maximum))
        if self.minimum and self.minimum > obj:
            raise ValidationException('The object is smaller than the required'
                                      ' minimum: {0} < {1}'.format(obj, self.minimum))

        # validation passed
        return obj

    def _type_helper(self, obj):
        if not isinstance(obj, six.integer_types):
            raise ValidationException('the object is not a valid integer type: {0}'.format(obj))
        return obj


class FloatField(IntegerField):
    def translate(self, obj):
        obj = super(FloatField, self).translate(obj)
        try:
            return float(obj)
        except ValueError:
            raise TranslationException('obj is not castable to float: {0}'.format(obj))

    def _type_helper(self, obj):
        if not isinstance(obj, float):
            raise ValidationException('obj is not a float type: {0}'.format(obj))
        return obj


class BooleanField(BaseField):
    # TODO
    def translate(self, obj):
        if isinstance(obj, bool):
            return obj
        if isinstance(obj, six.string_types):
            if obj.lower() == 'false':
                return False
            elif obj.lower() == 'true':
                return True
        raise ValidationException('{0} is not a valid boolean.  Either'
                                  ' "true" or "false" is required (case insensitive)'.format(obj))
