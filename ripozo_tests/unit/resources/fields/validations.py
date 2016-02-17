from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import unittest2

import mock

from ripozo.exceptions import ValidationException
from ripozo.resources.fields.field import Field
from ripozo.resources.fields.validations import translate_iterable_to_single, \
    validate_required, validate_type, validate_size, validate_regex, \
    basic_validation


class TestValidation(unittest2.TestCase):
    def test_translate_iterable_to_single(self):
        """
        Tests the case where the item is an iterable
        """
        resp = translate_iterable_to_single([1, 2])
        self.assertEqual(resp, 1)

    def test_translate_iterable_to_single_not_list(self):
        """
        Tests the case where the item is not an iterable
        """
        resp = translate_iterable_to_single(1)
        self.assertEqual(resp, 1)

    def test_validate_required_success(self):
        """
        Tests when the object is required and it is there
        """
        f = Field('f', required=True)
        resp = validate_required(f, 1)
        self.assertEqual(resp, 1)

    def test_validate_required_skipped(self):
        """
        Tests when the item is None and the validation is skipped
        because skip_required is True
        """
        f = Field('f', required=True)
        resp = validate_required(f, None, skip_required=True)
        self.assertEqual(resp, None)

    def test_validate_required_non_required_field(self):
        """
        Tests the the field is validated if the field
        is not required and the object is None
        """
        f = Field('f', required=False)
        resp = validate_required(f, None, skip_required=False)
        self.assertEqual(resp, None)

    def test_validate_required_failure(self):
        """Tests that it fails when the object is None"""
        f = Field('f', required=True)
        self.assertRaises(ValidationException, validate_required, f, None)

    def test_validate_type(self):
        """Success case for validate_type"""
        f = Field('f')
        obj = object()
        resp = validate_type(f, object, obj)
        self.assertIs(resp, obj)

    def test_validate_type_failure(self):
        """Failure case for validate_type"""
        f = Field('f')
        obj = 'blah'
        self.assertRaises(ValidationException, validate_type, f, int, obj)

    def test_validate_size(self):
        """Success case for validate size"""
        f = Field('blah')
        obj = 10
        resp = validate_size(f, obj, obj, minimum=10, maximum=10)
        self.assertEqual(resp, obj)

    def test_validate_size_too_small(self):
        f = Field('blah')
        obj = 10
        self.assertRaises(ValidationException, validate_size, f, obj, obj, minimum=11)

    def test_validate_size_too_large(self):
        f = Field('blah')
        obj = 10
        self.assertRaises(ValidationException, validate_size, f, obj, obj, maximum=9)

    def test_validate_regex(self):
        """Success case for validate_regex"""
        regex = re.compile(r'[a-z]*something[a-z]*')
        f = Field('f')
        obj = 'dfgfgfsomethingdfgfgfs'
        resp = validate_regex(f, obj, regex)
        self.assertEqual(resp, obj)

    def test_validate_regex_failure(self):
        """Failure case for validate_regex"""
        regex = re.compile(r'something')
        f = Field('f')
        obj = 'notthatsome'
        self.assertRaises(ValidationException, validate_regex, f, obj, regex)

    def test_validate_regex_multiple_matches(self):
        """Tests that the validation succeeds if there is more than one match"""
        regex = re.compile(r'something')
        f = Field('f')
        obj = 'somethingsomethingsomething'
        resp = validate_regex(f, obj, regex)
        self.assertEqual(resp, obj)

    def test_basic_validation(self):
        """Success case for basic_validation"""
        f = Field('f', required=True)
        obj = object()
        resp = basic_validation(f, obj, skip_required=False)
        self.assertIs(resp, obj)

    def test_basic_validation_skip_required(self):
        """Tests when skip_required is True and the object is None"""
        f = Field('f', required=True)
        resp = basic_validation(f, None, skip_required=True)
        self.assertIsNone(resp)

    @mock.patch('ripozo.resources.fields.validations.validate_type')
    def test_basic_validation_none_object(self, validate_type):
        """Check that validate_type is not called when object is None"""
        f = Field('f', required=True)
        basic_validation(f, None, skip_required=True)
        self.assertFalse(validate_type.called)

        # Also ensure that it is called
        basic_validation(f, object(), skip_required=True)
        self.assertTrue(validate_type.called)

    def test_basic_validation_required_failure(self):
        f = Field('f', required=True)
        self.assertRaises(ValidationException, basic_validation, f, None)

    def test_basic_validation_type_mismatch(self):
        class Temp(Field):
            field_type = dict

        f = Temp('f')
        self.assertRaises(ValidationException, basic_validation, f, object())
