from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from ripozo.exceptions import ValidationException, TranslationException
from ripozo.viewsets.constants.input_categories import QUERY_ARGS
from ripozo.viewsets.fields.base import BaseField

import six


class StringField(BaseField):
    """
    Used for casting and validating string fields.
    """
    field_type = six.text_type

    def __init__(self, name, default=None, required=False, maximum=None, minimum=None, arg_type=QUERY_ARGS, regex=None):
        """
        A field class for validating string inputs.

        :param arg_type:
        :param int min_length: The minimum legnth of the string
        :param _sre.SRE_Pattern regex: A compiled regular expression that must
            match at least once.
        """
        super(StringField, self).__init__(name, required=required, maximum=maximum,
                                          minimum=minimum, arg_type=arg_type, default=default)
        self.regex = regex

    def translate(self, obj):
        """
        Attempts to convert the object to a string type

        :param object obj:
        :return: The object in its string representation
        :rtype: unicode
        :raises: TranslationsException
        """
        # A none input should be handled by the validator
        if obj is None:
            return obj

        obj = super(StringField, self).translate(obj)
        try:
            return six.text_type(obj)
        except ValueError:
            raise TranslationException('obj is not a valid unicode string: {0}'.format(obj))

    def validate(self, obj):
        """
        Validates the object.  It makes a call to super checking if the input
        can be None

        :param unicode obj:
        :return:
        :rtype: unicode
        :raises: ValidationException
        """
        obj = super(StringField, self).validate(obj)
        if self._skip_validation(obj):
            return obj
        obj = self._validate_size(obj, len(obj))
        if self.regex and not self.regex.match(obj):
            raise ValidationException('The input string did not match the'
                                      ' required regex: {0} != {1}'.format(obj, self.regex))

        # passed validation
        return obj


class IntegerField(BaseField):
    """
    A field used for translating and validating an integer input
    """
    field_type = int

    def translate(self, obj):
        # A none input should be handled by the validator
        if obj is None:
            return obj

        obj = super(IntegerField, self).translate(obj)
        try:
            return int(obj)
        except ValueError:
            raise TranslationException('Not a valid integer type: {0}'.format(obj))

    def validate(self, obj):
        obj = super(IntegerField, self).validate(obj)
        if self._skip_validation(obj):
            return obj
        return self._validate_size(obj, obj)


class FloatField(IntegerField):
    """
    A field used for translating and validating a float input
    """
    field_type = float

    def translate(self, obj):
        # A none input should be handled by the validator
        if obj is None:
            return obj

        obj = super(IntegerField, self).translate(obj)
        try:
            return float(obj)
        except (ValueError, TypeError):
            raise TranslationException('obj is not castable to float: {0}'.format(obj))


class BooleanField(BaseField):
    """
    A field used for translating and validating a boolean input
    It can take either a boolean or a string.
    """
    field_type = bool

    def translate(self, obj):
        # A none input should be handled by the validator
        obj = super(BooleanField, self).translate(obj)
        if obj is None:
            return obj

        if isinstance(obj, bool):
            return obj
        if isinstance(obj, six.string_types):
            if obj.lower() == 'false':
                return False
            elif obj.lower() == 'true':
                return True
        raise TranslationException('{0} is not a valid boolean.  Either'
                                  ' "true" or "false" is required (case insensitive)'.format(obj))


class DateTimeField(BaseField):
    """
    A field for validating and translating a datetime input.
    By default it accepts the following formats:

    %Y-%m-%dT%H:%M:%S.%fZ

    If you need other formats simply pass a list of valid formats
    into the valid_formats parameter on initialization
    """
    field_type = datetime
    valid_formats = ['%Y-%m-%dT%H:%M:%S.%fZ']

    def __init__(self, name, required=False, maximum=None, minimum=None, arg_type=QUERY_ARGS, valid_formats=None):
        super(DateTimeField, self).__init__(name, required=required, maximum=maximum,
                                            minimum=minimum, arg_type=arg_type)
        if valid_formats is not None:
            self.valid_formats = valid_formats

    def translate(self, obj):
        """
        First checks if the obj is None or already a datetime object
        Returns that if true.  Otherwise assumes that it is a string
        and attempts to parse it out using the formats in self.valid_formats
        and the datetime.strptime method

        Additionally it strips out any whitespace from the beginning and
        end of the input before attempting to parse out a datetime string

        :param unicode obj: The input that is being translated
        :return: The parse datetime object
        :rtype: datetime
        """
        if obj is None or isinstance(obj, datetime):
            return obj
        obj = obj.strip()
        for f in self.valid_formats:
            try:
                return datetime.strptime(obj, f)
            except ValueError:
                continue
        raise TranslationException('The object ({0}) could not be parsed as a datetime '
                                   'string using the formats {1}'.format(obj, self.valid_formats))

    def validate(self, obj):
        """
        Just makes a size check on top of instance type check

        :param datetime obj:
        :return: The object unchanged
        :rtype: datetime
        :raises: ValidationException
        """
        obj = super(DateTimeField, self).validate(obj)
        return self._validate_size(obj, obj)
