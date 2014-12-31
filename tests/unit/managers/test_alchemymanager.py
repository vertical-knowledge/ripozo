__author__ = 'Tim Martin'
from tests.base import DummyModelsBase
from tests.unit.managers.test_manager_base import TestManagerBase, generate_random_name


class Person:
    pass


class PersonManager:
    pass


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