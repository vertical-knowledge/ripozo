from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException
from ripozo.viewsets.fields.base import BaseField
from tests.python2base import TestBase

import six


class TestBaseField(TestBase):
    def test_not_required(self):
        f = BaseField('field', required=False)
        obj = f.translate_and_validate(None)
        self.assertIsNone(obj)
        obj = f.translate(None)
        self.assertIsNone(obj)
        obj = f.validate(None)
        self.assertIsNone(obj)

        self.required_helper(f)

    def test_required(self):
        f = BaseField('field', required=True)
        self.assertRaises(ValidationException, f.translate_and_validate, None)
        self.assertRaises(ValidationException, f.validate, None)
        self.assertIsNone(f.translate(None))

        self.required_helper(f)

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

    def test_validate_size(self):
        f = BaseField('field', minimum=5, maximum=10)
        self.assertRaises(ValidationException, f._validate_size, None, -1)
        self.assertRaises(ValidationException, f._validate_size, None, 4)

        # Check to make sure it doesn't raise an exception
        f._validate_size(None, 5)
        f._validate_size(None, 8)
        f._validate_size(None, 10)

        self.assertRaises(ValidationException, f._validate_size, None, 11)

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

    def test_name(self):
        field_name = 'field'
        f = BaseField(field_name)
        self.assertEqual(f.name, field_name)
        self.assertEqual(field_name, six.text_type(f))
