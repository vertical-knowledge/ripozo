from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest2

from ripozo.resources.fields.validations import translate_iterable_to_single, \
    validate_required, validate_type, validate_size, validate_regex, \
    basic_validation


class TestValidation(unittest2.TestCase):
    def test_translate_iterable_to_single(self):
        """
        Tests the case where the item is an iterable
        """
        assert False

    def test_translate_iterable_to_single_not_list(self):
        """
        Tests the case where the item is not an iterable
        """
        assert False

    def test_validate_required_success(self):
        """
        Tests when the object is required and it is there
        """
        assert False

    def test_validate_required_skipped(self):
        """
        Tests when the item is None and the validation is skipped
        because skip_required is True
        """
        assert False

    def test_validate_required_failure(self):
        """Tests that it fails when the object is None"""
        assert False

    def test_validate_type(self):
        """Success case for validate_type"""
        assert False

    def test_validate_type_failure(self):
        """Failure case for validate_type"""
        assert False

    def test_validate_size(self):
        """Success case for validate size"""
        assert False

    def test_validate_size_too_small(self):
        assert False

    def test_validate_size_too_large(self):
        assert False

    def test_validate_regex(self):
        """Success case for validate_regex"""
        assert False

    def test_validate_regex_failuer(self):
        """Failure case for validate_regex"""
        assert False

    def test_validate_regex_multiple_matches(self):
        """Tests that the validation succeeds if there is more than one match"""
        assert False

    def test_basic_validation(self):
        """Success case for basic_validation"""
        assert False

    def test_basic_validation_none_object(self):
        """Check that validate_type is not called when object is None"""
        assert False

    def test_basic_validation_required_failure(self):
        assert False

    def test_basic_validation_type_mismatch(self):
        assert False
