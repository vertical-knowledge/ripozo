from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.resources.constructor import ResourceMetaClass

import mock
import six
import unittest2


class TestResourceMetaClass(unittest2.TestCase):
    def setUp(self):
        ResourceMetaClass.registered_names_map.clear()
        ResourceMetaClass.registered_resource_classes.clear()

    def test_new_resource_class(self):
        """
        Tests that a resource class is instantiated correctly.
        """
        class_name = b'MyClass' if six.PY2 else 'MyClass'
        klass = ResourceMetaClass(class_name, (object,), dict(base_url='blah'))
        self.assertIn(class_name, ResourceMetaClass.registered_names_map)
        self.assertIn(klass, ResourceMetaClass.registered_resource_classes)

    def test_new_resource_class_abstract(self):
        """
        Tests that a resource class is not instantiated
        if it has a new attribute __abstract__ = True
        """
        class_name = b'MyClass' if six.PY2 else 'MyClass'
        klass = ResourceMetaClass(class_name, (object,), dict(__abstract__=True))
        self.assertNotIn(class_name, ResourceMetaClass.registered_names_map)
        self.assertNotIn(klass, ResourceMetaClass.registered_resource_classes)

    def test_register_class_registration_dicts(self):
        """
        Tests that the side effects of registering
        a class works appropriately.
        """
        name = b'name' if six.PY2 else 'name'
        mck = mock.Mock(base_url='blah', __name__=name)
        ResourceMetaClass.register_class(mck)
        self.assertEqual(id(mck), id(ResourceMetaClass.registered_names_map[name]))
        self.assertEqual(mck.base_url, ResourceMetaClass.registered_resource_classes[mck])
