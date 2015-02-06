from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tests.python2base import TestBase
from tests.unit.helpers.inmemory_manager import InMemoryManager
from tests.unit.managers.test_manager_common import TestManagerMixin

import six


class TestManager(TestManagerMixin, TestBase):
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