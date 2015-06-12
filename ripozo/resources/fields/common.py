from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from ripozo.exceptions import ValidationException, TranslationException
from ripozo.resources.constants.input_categories import BODY_ARGS
from ripozo.resources.fields.base import BaseField

import six


class StringField(BaseField):
    """
    Used for casting and validating string fields.
    """
    field_type = six.text_type

    def __init__(self, name,  regex=None, **kwargs):
        """
        A field class for validating string inputs.

        :param unicode name: The name of the field
        :param _sre.SRE_Pattern regex: A compiled regular expression that must
            match at least once.
        :param dict kwargs:  The additional arguments to pass
            to the super call.
        """
        super(StringField, self).__init__(name, **kwargs)
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
    A field used for translating and validating an integer input.
    While translating it will attempt to cast the object provided
    as an integer.
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
    A field used for translating and validating a float input.
    Pretty much the same as the IntegerField except that it
    will be cast as an IntegerField.
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
    If it's a string it checks if it matches 'false' or
    'true' (case insensitive).
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
    def __init__(self, name, indv_field=BaseField('list'), **kwargs):
        """

        :param unicode name: The name of the field.
        :param BaseField indv_field: The field to use when
            translating and validating individual items
            in the list.
        """
        self.indv_field = indv_field
        super(ListField, self).__init__(name, **kwargs)

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
        obj = obj or []
        return self._validate_size(obj, len(obj), msg=self.error_message)


class DictField(BaseField):
    """
    A field for a dictionary of objects.  Each named
    sub-field can be mapped to individual fields (Or even
    nested DictField's).
    """
    field_type = dict

    def __init__(self, name, field_list=None, **kwargs):
        """
        Calls super and sets the field_dict on the object.

        :param unicode name: The name of this field.
        :param list field_list: A list of fields the names
            of the fields are what is used as the key in the dictionary.
        :param dict kwargs: The standard arguments for BaseField.__init__
        """
        self.field_list = field_list or []
        super(DictField, self).__init__(name, **kwargs)

    def translate(self, obj, **kwargs):
        """
        Translates and Validates the dictionary field and
        each of it's contained fields.  It will iterate over
        this field_dict and translate and validate each of the
        individual key, value pairs.

        :param dict obj: The object to translate and validate (if
            validate=True)
        :return: The translated (and possibly validated) object.
        :rtype: dict
        """
        obj = super(DictField, self).translate(obj, **kwargs)
        if obj is None:
            return obj
        translated_dict = obj.copy()
        for field in self.field_list:
            key = field.name
            value = obj.get(key, None)
            translated_dict[key] = field.translate(value, **kwargs)
        return translated_dict

    def _translate(self, obj, skip_required=False):
        if obj is None:  # let the validation handle it.
            return obj
        if not hasattr(obj, 'get'):
            raise TranslationException(self.error_message or 'A dictionary field must have a get method '
                                                             'that allows for retrieving an item with a default. '
                                                             'For example a dictionary.')
        return obj

    def _validate(self, obj, skip_required=False):
        obj = super(DictField, self)._validate(obj, skip_required=skip_required)
        obj = obj or {}
        return self._validate_size(obj, len(obj), msg=self.error_message)
