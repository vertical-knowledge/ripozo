from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from ripozo.exceptions import ValidationException, TranslationException
from ripozo.viewsets.constants.input_categories import BODY_ARGS
from ripozo.viewsets.fields.base import BaseField

import six


class StringField(BaseField):
    """
    Used for casting and validating string fields.
    """
    field_type = six.text_type

    def __init__(self, name, required=False, maximum=None, minimum=None,
                 arg_type=BODY_ARGS, regex=None, error_message=None):
        """
        A field class for validating string inputs.

        :param arg_type:
        :param int min_length: The minimum legnth of the string
        :param _sre.SRE_Pattern regex: A compiled regular expression that must
            match at least once.
        """
        super(StringField, self).__init__(name, required=required, maximum=maximum,
                                          minimum=minimum, arg_type=arg_type,
                                          error_message=error_message)
        self.regex = regex

    def _translate(self, obj, skip_required=False):
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

        obj = super(StringField, self)._translate(obj, skip_required=skip_required)
        return six.text_type(obj)

    def _validate(self, obj, skip_required=False):
        """
        Validates the object.  It makes a call to super checking if the input
        can be None

        :param unicode obj:
        :return:
        :rtype: unicode
        :raises: ValidationException
        """
        obj = super(StringField, self)._validate(obj, skip_required=skip_required)
        if self._skip_validation(obj):
            return obj
        obj = self._validate_size(obj, len(obj))
        if self.regex and not self.regex.match(obj):
            raise ValidationException(self.error_message or 'The input string did not match the'
                                      ' required regex: {0} != {1}'.format(obj, self.regex))

        # passed validation
        return obj


class IntegerField(BaseField):
    """
    A field used for translating and validating an integer input
    """
    field_type = int

    def _translate(self, obj, skip_required=False):
        # A none input should be handled by the validator
        if obj is None:
            return obj

        obj = super(IntegerField, self)._translate(obj, skip_required=skip_required)
        try:
            return int(obj)
        except ValueError:
            raise TranslationException(self.error_message or
                                       'Not a valid integer type: {0}'.format(obj))

    def _validate(self, obj, skip_required=False):
        obj = super(IntegerField, self)._validate(obj, skip_required=skip_required)
        if self._skip_validation(obj):
            return obj
        return self._validate_size(obj, obj)


class FloatField(IntegerField):
    """
    A field used for translating and validating a float input
    """
    field_type = float

    def _translate(self, obj, skip_required=False):
        # A none input should be handled by the validator
        if obj is None:
            return obj

        obj = super(IntegerField, self)._translate(obj, skip_required=skip_required)
        try:
            return float(obj)
        except (ValueError, TypeError):
            raise TranslationException(self.error_message or
                                       'obj is not castable to float: {0}'.format(obj))


class BooleanField(BaseField):
    """
    A field used for translating and validating a boolean input
    It can take either a boolean or a string.
    """
    field_type = bool

    def _translate(self, obj, skip_required=False):
        # A none input should be handled by the validator
        obj = super(BooleanField, self)._translate(obj, skip_required=skip_required)
        if obj is None:
            return obj

        if isinstance(obj, bool):
            return obj
        if isinstance(obj, six.string_types):
            if obj.lower() == 'false':
                return False
            elif obj.lower() == 'true':
                return True
        raise TranslationException(self.error_message or
                                   '{0} is not a valid boolean.  Either'
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

    def __init__(self, name, required=False, maximum=None, minimum=None, arg_type=BODY_ARGS,
                 valid_formats=None, error_message=None):
        """
        :param unicode name: The name of the field
        :param bool required: Whether the field is required
        :param datetime maximum: The field must be less than the maximum
        :param datetime minimum: The input must be greater than this
        :param unicode arg_type: Where the input should be put
        :param list valid_formats: A list of datetime formats that are valid
            for translation. By default it accepts %Y-%m-%dT%H:%M:%S.%fZ
        :param unicode error_message: The error message to be returned if the
            validation or translation fails.
        """
        super(DateTimeField, self).__init__(name, required=required, maximum=maximum,
                                            minimum=minimum, arg_type=arg_type,
                                            error_message=error_message)
        self.valid_formats = valid_formats or self.valid_formats

    def _translate(self, obj, skip_required=False):
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
        raise TranslationException(self.error_message or
                                   'The object ({0}) could not be parsed as a datetime '
                                   'string using the formats {1}'.format(obj, self.valid_formats))

    def _validate(self, obj, skip_required=False):
        """
        Just makes a size check on top of instance type check

        :param datetime obj:
        :return: The object unchanged
        :rtype: datetime
        :raises: ValidationException
        """
        obj = super(DateTimeField, self)._validate(obj, skip_required=skip_required)
        return self._validate_size(obj, obj)


class ListField(BaseField):
    """
    A field for a list of objects.  A field for the individual
    results can also be provided.  This would be run against
    every individual item in the list that is provided.
    """
    field_type = list

    # TODO test and finish docs
    def __init__(self, name, required=False, maximum=None,
                 minimum=None, arg_type=BODY_ARGS,
                 error_message=None, indv_field=BaseField('list')):
        self.indv_field = indv_field
        super(ListField, self).__init__(name, required=required, maximum=maximum,
                                        minimum=minimum, arg_type=arg_type,
                                        error_message=error_message)

    def translate(self, obj, skip_required=False, validate=False):
        obj = super(ListField, self).translate(obj, skip_required=skip_required, validate=validate)
        if obj is None:
            return obj
        translated_list = []
        for f in obj:
            translated_list.append(self.indv_field.translate(f, skip_required=skip_required, validate=validate))
        return translated_list

    def _translate(self, obj, skip_required=False):
        if obj is None:  # let the validation handle it.
            return obj
        if not isinstance(obj, (list, set, tuple,)):
            raise TranslationException(self.error_message or 'A list field must be an instance of a list, '
                                                             'tuple, or set')
        return obj

    def _validate(self, obj, skip_required=False):
        obj = super(ListField, self)._validate(obj, skip_required=skip_required)
        if not obj:
            obj = []
        return self._validate_size(obj, len(obj), msg=self.error_message)
