from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import six
import unittest2

from ripozo.resources.fields.base import BaseField
from ripozo.manager_base import BaseManager
from ripozo_tests.helpers.inmemory_manager import InMemoryManager


class TestManager(unittest2.TestCase):
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

    def test_field_validators(self):
        """
        Test the field_validators class property

        :param mock.MagicMock mck:
        """
        class MyManager(InMemoryManager):
            get_field_type = mock.MagicMock()
            pass
        self.assertIsNone(MyManager._field_validators)
        self.assertListEqual(MyManager.field_validators, [])

        class MyManager(MyManager):
            fields = [1, 2, 3]

        fields = MyManager.fields

        mck_list = MyManager.field_validators
        self.assertIsInstance(mck_list, list)
        self.assertEqual(MyManager.get_field_type.call_count, len(fields))
        args = list((x[0][0] for x in MyManager.get_field_type.call_args_list))
        self.assertListEqual(args, fields)

    def test_list_fields_property(self):
        """
        Tests whether the list_fields property appropriately
        gets the list_fields in all circumstances
        """
        _fields = [1, 2, 3]
        _list_fields = [4, 5]

        class M1(InMemoryManager):
            fields = _fields
            list_fields = _list_fields

        self.assertListEqual(_list_fields, M1.list_fields)
        self.assertListEqual(_fields, M1.fields)
        self.assertNotEqual(M1.list_fields, M1.fields)

        class M2(InMemoryManager):
            fields = _fields

        self.assertListEqual(_fields, M2.fields)
        self.assertListEqual(_fields, M2.list_fields)
        self.assertListEqual(M2.fields, M2.list_fields)

    def test_abstact_method_pissing_me_off(self):
        class Manager(InMemoryManager):
            pass

        self.assertIsInstance(super(Manager, Manager()).get_field_type('blah'), BaseField)

    def test_update_fields(self):
        """
        Tests the update_fields class property
        """

        class Manager(InMemoryManager):
            fields = ('id', 'another', 'final',)

        self.assertTupleEqual(Manager.fields, Manager.update_fields)
