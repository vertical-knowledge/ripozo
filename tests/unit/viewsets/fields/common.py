from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException, TranslationException
from ripozo.viewsets.fields.common import StringField, BooleanField, FloatField, DateTimeField, IntegerField
from tests.python2base import TestBase

import datetime
import re
import six


class CommonMixin(object):
    field_type = None
    instance_type = None
    translation_failures = []
    translation_success = []

    def test_not_required(self):
        f = self.field_type('field', required=False)
        obj = f.translate_and_validate(None)
        self.assertIsNone(obj)
        obj = f.translate(None)
        self.assertIsNone(obj)
        obj = f.validate(None)
        self.assertIsNone(obj)

    def test_required(self):
        f = self.field_type('field', required=True)
        self.assertRaises(ValidationException, f.translate_and_validate, None)
        self.assertRaises(ValidationException, f.validate, None)
        self.assertIsNone(f.translate(None))

    def size_test_helper(self, too_small, valid, too_large, minimum=5, maximum=10):
        f = self.field_type('field', minimum=minimum, maximum=maximum)
        self.assertRaises(ValidationException, f.validate, too_small)

        obj = f.validate(valid)
        self.assertEqual(valid, obj)

        self.assertRaises(ValidationException, f.validate, too_large)

    def test_translation_failure(self):
        f = self.field_type('field')
        for failure in self.translation_failures:
            self.assertRaises(TranslationException, f.translate, failure)
            self.assertRaises(TranslationException, f.translate_and_validate, failure)

    def test_translation_success(self):
        f = self.field_type('field')
        for success in self.translation_success:
            new = f.translate(success)
            self.assertIsInstance(new, self.instance_type)

    def test_translate_none(self):
        """Tests whether the field can appropriately handle None, False, etc"""
        f = self.field_type('field')
        output = f.translate(None)
        self.assertIsNone(output)


class StringFieldTest(TestBase, CommonMixin):
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


class IntegerFieldTest(TestBase, CommonMixin):
    field_type = IntegerField
    instance_type = int
    translation_success = [1, '123', 1.5]
    translation_failures = ['abc', '']  # everything should be convertable to a string

    def test_size(self):
        self.size_test_helper(1, 7, 12)


class FloatFieldTest(TestBase, CommonMixin):
    field_type = FloatField
    instance_type = float
    translation_success = [1, '1', 1.5]
    translation_failures = ['abc', '']  # everything should be convertable to a string

    def test_size(self):
        self.size_test_helper(1.0, 7.0, 12.0)


class BoolFieldTest(TestBase, CommonMixin):
    field_type = BooleanField
    instance_type = bool
    translation_success = [True, False, 'True', 'False', 'true', 'false', 'TRUE', 'FALSE']
    translation_failures = ['somethingelse', 0]  # everything should be convertable to a string


class DatetimeFieldTest(TestBase, CommonMixin):
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
