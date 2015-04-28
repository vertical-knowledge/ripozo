from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import NotFoundException
from ripozo.managers.base import BaseManager
from uuid import uuid1
import six

__author__ = 'Tim Martin'


class InMemoryManager(BaseManager):
    objects = None
    _model_name = 'Fake'

    def __init__(self):
        super(InMemoryManager, self).__init__()
        self.objects = {}

    def create(self, values, *args, **kwargs):
        super(InMemoryManager, self).create(values, *args, **kwargs)
        new_id = uuid1()
        values['id'] = new_id
        self.queryset[new_id] = values
        return values

    def retrieve_list(self, filters, *args, **kwargs):
        super(InMemoryManager, self).retrieve_list(filters, *args, **kwargs)
        pagination_page, filters = self.get_pagination_pks(filters)
        if not pagination_page:
            pagination_page = 0
        pagination_count, filters = self.get_pagination_count(filters)
        values = list(six.itervalues(self.queryset))
        first = pagination_page * pagination_count
        last = first + pagination_count
        if last > len(values):
            values = values[first:]
            pagination_page = None
        else:
            values = values[first:last]
            pagination_page += 1
        return values, {self.pagination_next: None,
                        self.pagination_pk_query_arg: pagination_page,
                        self.pagination_count_query_arg: pagination_count}

    @property
    def queryset(self):
        super(InMemoryManager, self).queryset
        return self.objects

    def retrieve(self, lookup_keys, *args, **kwargs):
        super(InMemoryManager, self).retrieve(lookup_keys, *args, **kwargs)
        return self._get_model(lookup_keys)

    @property
    def model_name(self):
        return self._model_name

    def update(self, lookup_keys, updates, *args, **kwargs):
        super(InMemoryManager, self).update(lookup_keys, updates, *args, **kwargs)
        obj = self._get_model(lookup_keys)
        for key, value in six.iteritems(updates):
            obj[key] = value
        self.queryset[lookup_keys['id']] = obj
        return obj

    def get_field_type(self, name):
        super(InMemoryManager, self).get_field_type(name)
        pass

    def delete(self, lookup_keys, *args, **kwargs):
        super(InMemoryManager, self).delete(lookup_keys, *args, **kwargs)
        self.queryset.pop(lookup_keys['id'])
        return None

    def _get_model(self, model_id):
        obj = self.queryset.get(model_id['id'], None)
        if not obj:
            raise NotFoundException
        return obj


class PersonInMemoryManager(InMemoryManager):
    model = 'Something'
    _model_name = 'Person'