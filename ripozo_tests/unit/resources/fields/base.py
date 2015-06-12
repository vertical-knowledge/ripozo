from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest2

from ripozo.exceptions import ValidationException, TranslationException, RestException
from ripozo.resources.constants import input_categories
from ripozo.resources.fields.base import BaseField, translate_fields
from ripozo import RequestContainer
from ripozo_tests.bases.field import FieldTestBase


class FieldTestBase2(FieldTestBase):
    validation_exception = ValidationException
    translation_exception = TranslationException


class TestBaseField(FieldTestBase2, unittest2.TestCase):
    field_type = BaseField
    instance_type = object

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
        output = f._translate(False)
        self.assertIsNotNone(output)
        self.assertFalse(output)

    def test_empty_list(self):
        f = BaseField('field')
        output = f._translate([])
        self.assertIsNone(output)


class TestTranslateFields(unittest2.TestCase):
    """
    For testing the translate_fields method.
    """

    def test_required(self):
        field = BaseField('field', required=True)
        req = RequestContainer()
        self.assertRaises(ValidationException, translate_fields, req,
                          fields=[field], validate=True)
        test_body = dict(nothere='this')
        req = RequestContainer(body_args=test_body)
        url, query, body = translate_fields(req, fields=[field], validate=True, skip_required=True)
        self.assertEqual(body, test_body)

    def test_input_category_types(self):
        cat = input_categories.URL_PARAMS
        test_input = dict(field='something')

        # URL_PARAMS
        field = BaseField('field', required=True, arg_type=input_categories.URL_PARAMS)
        req = RequestContainer(url_params=test_input)
        url, query, body = translate_fields(req, fields=[field], validate=True)
        self.assertEqual(url, test_input)
        req = RequestContainer(query_args=test_input, body_args=test_input)
        self.assertRaises(ValidationException, translate_fields, req,
                          fields=[field], validate=True)

        # QUERY_ARGS
        field = BaseField('field', required=True, arg_type=input_categories.QUERY_ARGS)
        req = RequestContainer(query_args=test_input)
        url, query, body = translate_fields(req, fields=[field], validate=True)
        self.assertEqual(query, test_input)
        req = RequestContainer(url_params=test_input, body_args=test_input)
        self.assertRaises(ValidationException, translate_fields, req,
                          fields=[field], validate=True)

        # BODY_ARGS
        field = BaseField('field', required=True, arg_type=input_categories.BODY_ARGS)
        req = RequestContainer(body_args=test_input)
        url, query, body = translate_fields(req, fields=[field], validate=True)
        self.assertEqual(body, test_input)
        req = RequestContainer(query_args=test_input, url_params=test_input)
        self.assertRaises(ValidationException, translate_fields, req,
                          fields=[field], validate=True)

        # Non-existent input type
        field = BaseField('field', required=True, arg_type='fake')
        req = RequestContainer(query_args=test_input, url_params=test_input, body_args=test_input)
        self.assertRaises(RestException, translate_fields, req, fields=[field], validate=True)
