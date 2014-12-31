__author__ = 'Tim Martin'
from cqlengine.exceptions import LWTException
from cqlengine.query import DoesNotExist
from tests.base import DummyModelsBase
from tests.integration.helpers.managers import PersonManager
from tests.test_models import Person
from tests.unit.managers.test_manager_base import TestManagerBase, generate_random_name


class TestCQLManagerBase(DummyModelsBase, TestManagerBase):
    @property
    def manager(self):
        return PersonManager()

    @property
    def all_person_models(self):
        return Person.objects.all()

    def get_person_model_by_id(self, person_id):
        return Person.objects.filter(id=person_id).get()

    @property
    def does_not_exist_exception(self):
        return DoesNotExist

    def test_create_on_existing_failure(self):
        """
        Tests the transaction statement that prevents creation if the model already exists
        """
        manager = self._manager
        manager.fail_create_if_exists = True
        p = manager.create({self.first_name_field: generate_random_name(),
                            self.last_name_field: generate_random_name()})
        self.assertRaises(LWTException, manager.create,
                          {self.id_field: p.get('id'),
                           self.first_name_field: generate_random_name(),
                           self.last_name_field: generate_random_name()})

    def test_create_on_existing_success(self):
        """
        Tests to ensure that the model gets overridden if .fail_create_if_exists is false
        """
        manager = self._manager
        manager.fail_create_if_exists = False
        p = manager.create({self.first_name_field: generate_random_name(),
                            self.last_name_field: generate_random_name()})
        p2 = manager.create({self.id_field: p.get('id'),
                             self.first_name_field: generate_random_name(),
                             self.last_name_field: generate_random_name()})
        self.assertEqual(p.get(self.id_field), p2.get(self.id_field))
        self.assertNotEqual(p[self.first_name_field], p2[self.first_name_field])
        self.assertNotEqual(p[self.last_name_field], p2[self.last_name_field])