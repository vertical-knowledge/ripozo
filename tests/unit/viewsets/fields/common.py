from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException, TranslationException
from ripozo.viewsets.fields.common import StringField, BooleanField, FloatField, DateTimeField, IntegerField, BaseField
from ripozo_tests.bases.field import FieldTestBase

import datetime
import re
import six
import unittest


# TODO test validating, translating, etc on multiple fields.
# TODO test field values that evaluate to None

class FieldTestBase2(FieldTestBase):
    validation_exception = ValidationException
    translation_exception = TranslationException


class TestBaseField(FieldTestBase2, unittest.TestCase):
    field_type = BaseField
    instance_type = object

    def required_helper(self, f):
        original = object()
        new = f.translate_and_validate(original)
        self.assertEqual(original, new)

        original = object()
        new = f.translate(original)
        self.assertEqual(original, new)

        original = object()
        new = f.validate(original)
        self.assertEqual(original, new)

    def test_validate_type(self):
        f = BaseField('field', required=False)
        original = object()

        # test doesn't raise when valid
        new = f._validate_type(None)
        self.assertIsNone(new)
        new = f._validate_type(original)
        self.assertEqual(new, original)

        f.field_type = int
        self.assertRaises(ValidationException, f._validate_type, 'something')

    def test_translate_none_like(self):
        f = BaseField('field')
        output = f.translate(False)
        self.assertIsNotNone(output)
        self.assertFalse(output)


class StringFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = StringField
    instance_type = six.text_type
    translation_success = ['', 'another', 1, True]
    translation_failures = []  # everything should be convertable to a string

    def test_size(self):
        self.size_test_helper('a', '123456', 'woooooooooooooooo')

    def test_validate_regex(self):
        f = StringField('field', regex=re.compile(r'^something$'))
        self.assertRaises(ValidationException, f.validate, 'notsomething')
        original = 'something'
        new = f.validate(original)
        self.assertEqual(original, new)


class IntegerFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = IntegerField
    instance_type = int
    translation_success = [1, '123', 1.5]
    translation_failures = ['abc', '']  # everything should be convertable to a string

    def test_size(self):
        self.size_test_helper(1, 7, 12)


class FloatFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = FloatField
    instance_type = float
    translation_success = [1, '1', 1.5]
    translation_failures = ['abc', '']  # everything should be convertable to a string

    def test_size(self):
        self.size_test_helper(1.0, 7.0, 12.0)


class BoolFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = BooleanField
    instance_type = bool
    translation_success = [True, False, 'True', 'False', 'true', 'false', 'TRUE', 'FALSE']
    translation_failures = ['somethingelse', 0]  # everything should be convertable to a string


class DatetimeFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = DateTimeField
    instance_type = datetime.datetime
    translation_success = [datetime.datetime.now(), '2015-02-10T18:15:15.123456Z']
    translation_failures = ['something', '2/15/2012']  # everything should be convertable to a string

    def test_size(self):
        minimum = datetime.datetime.now()
        maximum = minimum + datetime.timedelta(days=5)
        too_small = minimum - datetime.timedelta(days=5)
        too_large = maximum + datetime.timedelta(days=5)
        just_right = minimum + datetime.timedelta(days=2)
        self.size_test_helper(too_small, just_right, too_large, minimum=minimum, maximum=maximum)

    def test_valid_formats(self):
        d = '12/15/2015'
        valid_formats = ['%Y-%m-%dT%H:%M:%S.%fZ', '%m/%d/%Y']
        f = DateTimeField('field', valid_formats=valid_formats)
        inst = f.translate(d)
        self.assertIsInstance(inst, datetime.datetime)
        d = '2015-02-10T18:15:15.123456Z'
        inst = f.translate(d)
        self.assertIsInstance(inst, datetime.datetime)

        self.assertRaises(TranslationException, f.translate, '15/12/2015')
