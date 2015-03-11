from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo_tests.python2base import TestBase
from ripozo_tests.bases.manager import TestManagerMixin
from ripozo_tests.helpers.inmemory_manager import InMemoryManager

import mock
import six
import unittest


class TestManager(TestManagerMixin, TestBase, unittest.TestCase):
    @property
    def manager(self):
        """
        Return the serializer for the specific implementation

        :rtype: InMemoryManager
        """
        return InMemoryManager()

    @property
    def does_not_exist_exception(self):
        """
        return the exception type that is raised when the model does not exist
        """
        return KeyError

    @property
    def all_person_models(self):
        """
        :return: Every single person model
        :rtype: list
        """
        return list(six.itervalues(self._manager.objects))

    def get_person_model_by_id(self, person_id):
        """
        Directly query the data base for a person model with the id specified
        """
        return self._manager.objects[person_id]

    @mock.patch.object(InMemoryManager, 'get_field_type')
    def test_field_validators(self, mck):
        """
        Test the field_validators class property

        :param mock.MagicMock mck:
        """
        self.assertIsNone(InMemoryManager._field_validators)
        self.assertListEqual(InMemoryManager.field_validators, [])

        fields = [1, 2, 3]
        InMemoryManager._fields = fields

        mck_list = InMemoryManager.field_validators
        self.assertIsInstance(mck_list, list)
        self.assertEqual(mck.call_count, len(fields))
        args = list((x[0][0] for x in mck.call_args_list))
        self.assertListEqual(args, fields)