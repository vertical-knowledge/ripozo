from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import unittest2

from ripozo.exceptions import ValidationException
from ripozo.resources.fields.field import IField, Field


class TestField(unittest2.TestCase):
    def test_instantiate_ifield_error(self):
        """Ensure that the abstract base class raises a TypeError
        if you try to instantiate it directly"""
        self.assertRaises(TypeError, IField, 'f')

    def test_field_translate(self):
        f = Field('f')
        obj = object()
        resp = f.translate(obj)
        self.assertIs(obj, resp)

    def test_field_translate_none(self):
        f = Field('f', required=True)
        self.assertRaises(ValidationException, f.translate, None, validate=True)
        resp = f.translate(None, validate=False)
        self.assertIsNone(resp)

    def test_translate_not_implemented_error(self):
        class Temp(IField):
            def _translate(self, obj, skip_required=False):
                super(Temp, self)._translate(obj, skip_required=skip_required)

            def _validate(self, obj, skip_required=False):
                pass

        f = Temp('f')
        self.assertRaises(NotImplementedError, f._translate, 'something')

    def test_validate_not_implemented_error(self):
        class Temp(IField):
            def _translate(self, obj, skip_required=False):
                pass

            def _validate(self, obj, skip_required=False):
                super(Temp, self)._validate(obj, skip_required=skip_required)

        f = Temp('f')
        self.assertRaises(NotImplementedError, f._validate, 'something')
