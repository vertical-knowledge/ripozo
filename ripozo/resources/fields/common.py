"""
Contains common field types that
may be used.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
from datetime import datetime

from ripozo.exceptions import TranslationException
from ripozo.resources.fields.base import BaseField
from ripozo.resources.fields.field import IField, Field
from ripozo.resources.fields.validations import validate_regex, validate_size, \
    basic_validation, translate_iterable_to_single, validate_required

import six


class StringField(IField):
    """
    Used for casting and validating string fields.
    """
    field_type = six.text_type

    def __init__(self, name, regex=None, minimum=None, maximum=None, **kwargs):
        """
        A field class for validating string inputs.

        :param unicode name: The name of the field
        :param _sre.SRE_Pattern regex: A compiled regular expression that must
            match at least once.
        :param dict kwargs:  The additional arguments to pass
            to the super call.
        """
        super(StringField, self).__init__(name, **kwargs)
        self.minimum = minimum
        self.maximum = maximum
        self.regex = regex

    def _translate(self, obj, skip_required=False):
        """
        Attempts to convert the object to a string type

        :param object obj:
        :return: The object in its string representation
        :rtype: unicode
        :raises: TranslationsException
        """
        obj = translate_iterable_to_single(obj)
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
        obj = basic_validation(self, obj, skip_required=skip_required)
        if obj is None:
            return obj
        obj = validate_size(self, obj, len(obj),
                            minimum=self.minimum,
                            maximum=self.maximum,
                            msg=self.error_message)
        obj = validate_regex(self, obj, regex=self.regex)
        return obj


@six.add_metaclass(abc.ABCMeta)
class _INumberField(IField):
    @abc.abstractproperty
    def field_type(self):
        raise NotImplementedError

    def __init__(self, name, regex=None, minimum=None, maximum=None, **kwargs):
        super(_INumberField, self).__init__(name, **kwargs)
        self.minimum = minimum
        self.maximum = maximum
        self.regex = regex

    def _translate(self, obj, skip_required=False):
        obj = translate_iterable_to_single(obj)
        try:
            return self.field_type(obj)
        except ValueError:
            msg = self.error_message or 'Not a valid integer type: {0}'.format(obj)
            raise TranslationException(msg)

    def _validate(self, obj, skip_required=False):
        obj = basic_validation(self, obj, skip_required=skip_required)
        if obj is None:
            return obj
        obj = validate_size(self, obj, obj,
                            minimum=self.minimum,
                            maximum=self.maximum,
                            msg=self.error_message)
        return obj


class IntegerField(_INumberField):
    """
    A field used for translating and validating an integer input.
    While translating it will attempt to cast the object provided
    as an integer.
    """
    field_type = int


class FloatField(_INumberField):
    """
    A field used for translating and validating a float input.
    Pretty much the same as the IntegerField except that it
    will be cast as an IntegerField.
    """
    field_type = float


class BooleanField(IField):
    """
    A field used for translating and validating a boolean input
    It can take either a boolean or a string.
    If it's a string it checks if it matches 'false' or
    'true' (case insensitive).
    """
    field_type = bool

    def _translate(self, obj, skip_required=False):
        obj = translate_iterable_to_single(obj)

        if isinstance(obj, bool):
            return obj
        if isinstance(obj, six.string_types):
            if obj.lower() == 'false':
                return False
            elif obj.lower() == 'true':
                return True
        msg = self.error_message or ('{0} is not a valid boolean.'
                                     '  Either "true" or "false" is '
                                     'required (case insensitive)'.format(obj))
        raise TranslationException(msg)

    def _validate(self, obj, skip_required=False):
        return validate_required(self, obj, skip_required=skip_required)


class DateTimeField(IField):
    """
    A field for validating and translating a datetime input.
    By default it accepts the following formats:

    %Y-%m-%dT%H:%M:%S.%fZ

    If you need other formats simply pass a list of valid formats
    into the valid_formats parameter on initialization
    """
    field_type = datetime
    valid_formats = ['%Y-%m-%dT%H:%M:%S.%fZ']

    def __init__(self, name, valid_formats=None, minimum=None, maximum=None, **kwargs):
        """
        :param unicode name: The name of the field
        :param list valid_formats: A list of datetime formats that are valid
            for translation. By default it accepts %Y-%m-%dT%H:%M:%S.%fZ
        """
        super(DateTimeField, self).__init__(name, **kwargs)
        self.valid_formats = valid_formats or self.valid_formats
        self.minimum = minimum
        self.maximum = maximum

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
        if isinstance(obj, datetime):
            return obj
        obj = obj.strip()
        for date_format in self.valid_formats:
            try:
                return datetime.strptime(obj, date_format)
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
        obj = basic_validation(self, obj, skip_required=skip_required)
        return validate_size(self, obj, obj,
                             minimum=self.minimum,
                             maximum=self.maximum,
                             msg=self.error_message)


class ListField(IField):
    """
    A field for a list of objects.  A field for the individual
    results can also be provided.  This would be run against
    every individual item in the list that is provided.
    """
    field_type = list

    def __init__(self, name, indv_field=None, minimum=None, maximum=None, **kwargs):
        """

        :param unicode name: The name of the field.
        :param BaseField indv_field: The field to use when
            translating and validating individual items
            in the list.
        """
        self.indv_field = indv_field or Field('list')
        super(ListField, self).__init__(name, **kwargs)
        self.minimum = minimum
        self.maximum = maximum

    def translate(self, obj, **kwargs):
        """
        Translates the object into a list.

        :param object obj: The object to translate.
        :return: The translated/validated object.
        :rtype: list
        """
        obj = super(ListField, self).translate(obj, **kwargs)
        if obj is None:
            return obj
        translated_list = []
        for field in obj:
            translated_field = self.indv_field.translate(field, **kwargs)
            translated_list.append(translated_field)
        return translated_list

    def _translate(self, obj, skip_required=False):
        try:
            return list(obj)
        except TypeError:
            raise TranslationException(self.error_message or
                                       '{0} requires an iterable. The object'
                                       ' {1} is not'.format(self.name, obj))

    def _validate(self, obj, skip_required=False):
        obj = basic_validation(self, obj, skip_required=skip_required)
        obj = obj or []
        return validate_size(self, obj, len(obj),
                             minimum=self.minimum,
                             maximum=self.maximum,
                             msg=self.error_message)


class DictField(IField):
    """
    A field for a dictionary of objects.  Each named
    sub-field can be mapped to individual fields (Or even
    nested DictField's).
    """
    field_type = dict

    def __init__(self, name, field_list=None, minimum=None, maximum=None, **kwargs):
        """
        Calls super and sets the field_dict on the object.

        :param unicode name: The name of this field.
        :param list field_list: A list of fields the names
            of the fields are what is used as the key in the dictionary.
        :param dict kwargs: The standard arguments for BaseField.__init__
        """
        self.field_list = field_list or []
        super(DictField, self).__init__(name, **kwargs)
        self.minimum = minimum
        self.maximum = maximum

    def translate(self, obj, **kwargs):
        """
        Translates and Validates the dictionary field and
        each of it's contained fields.  It will iterate over
        this field_dict and translate and validate each of the
        individual key, value pairs.

        :param dict obj: The object to translate and validate (if
            ``validate=True``)
        :return: The translated (and possibly validated) object.
        :rtype: dict
        """
        obj = super(DictField, self).translate(obj, **kwargs)
        if obj is None:
            return obj
        translated_dict = obj.copy()
        for field in self.field_list:
            key = field.name
            value = obj.get(key)
            translated_dict[key] = field.translate(value, **kwargs)
        return translated_dict

    def _translate(self, obj, skip_required=False):
        if not hasattr(obj, 'get'):
            raise TranslationException(self.error_message or
                                       'A dictionary field must have a get method '
                                       'that allows for retrieving an item with a default. '
                                       'For example a dictionary.')
        return obj

    def _validate(self, obj, skip_required=False):
        obj = basic_validation(self, obj, skip_required=skip_required)
        obj = obj or {}
        return validate_size(self, obj, len(obj),
                             minimum=self.minimum,
                             maximum=self.maximum,
                             msg=self.error_message)
