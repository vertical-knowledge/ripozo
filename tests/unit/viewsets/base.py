__author__ = 'Tim Martin'
from rest.managers.base import BaseManager, NotFoundException
import unittest
from uuid import uuid1


class InMemoryManager(BaseManager):
    objects = None
    _model_name = 'Fake'

    def __init__(self):
        super(InMemoryManager, self).__init__()
        self.objects = {}

    def create(self, values, *args, **kwargs):
        new_id = uuid1()
        values['id'] = new_id
        self.queryset[new_id] = values
        return values

    def retrieve_list(self, filters, *args, **kwargs):
        return self.queryset.values(), {self.pagination_next: None,
                                        self.pagination_pk_query_arg: None,
                                        self.pagination_count_query_arg: None}

    @property
    def queryset(self):
        return self.objects

    def retrieve(self, lookup_keys, *args, **kwargs):
        return self._get_model(lookup_keys)

    @property
    def model_name(self):
        return self._model_name

    def update(self, lookup_keys, updates, *args, **kwargs):
        obj = self._get_model(lookup_keys)
        for key, value in updates.iteritems():
            obj.set(key, value)
        self.queryset[lookup_keys] = obj
        return obj

    def get_field_type(self, name):
        pass

    def delete(self, lookup_keys, *args, **kwargs):
        self.queryset.pop(lookup_keys)
        return None

    def _get_model(self, model_id):
        obj = self.queryset.get(model_id, None)
        if not obj:
            raise NotFoundException
        return obj


class PersonInMemoryManager(InMemoryManager):
    model = 'Something'
    _model_name = 'Person'


class TesAPIBase(unittest.TestCase):
    def test_something(self):
        pass