from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class FieldTestBase(object):
    field_type = None
    instance_type = None
    translation_failures = []
    translation_success = []
    validation_exception = None
    translation_exception = None

    def test_name(self):
        field_name = 'field'
        f = self.field_type(field_name)
        self.assertEqual(f.name, field_name)

    def test_not_required(self):
        f = self.field_type('field', required=False)
        obj = f.translate(None, validate=True)
        self.assertIsNone(obj)
        obj = f.translate(None)
        self.assertIsNone(obj)
        obj = f.translate(None, validate=True)
        self.assertIsNone(obj)

    def test_required(self):
        f = self.field_type('field', required=True)
        self.assertRaises(self.validation_exception, f.translate, None, validate=True)
        self.assertIsNone(f.translate(None))

    def size_test_helper(self, too_small, valid, too_large, minimum=5, maximum=10):
        f = self.field_type('field', minimum=minimum, maximum=maximum)
        self.assertRaises(self.validation_exception, f.translate, too_small, validate=True)

        obj = f.translate(valid, validate=True)
        self.assertEqual(valid, obj)

        self.assertRaises(self.validation_exception, f.translate, too_large, validate=True)

    def test_translation_failure(self):
        f = self.field_type('field')
        for failure in self.translation_failures:
            self.assertRaises(self.translation_exception, f.translate, failure)
            self.assertRaises(self.translation_exception, f.translate, failure, validate=True)

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
