from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import NotFoundException
from ripozo.managers.base import BaseManager
from ripozo.resources.fields.base import BaseField
from uuid import uuid1
import six

__author__ = 'Tim Martin'


class InMemoryManager(BaseManager):
    # TODO redo this suite taking into account the
    # TODO TestManagerMixin (i.e. don't use the InMemoryManager)
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
        original_page = pagination_page
        values = list(six.itervalues(self.queryset))
        first = pagination_page * pagination_count
        last = first + pagination_count
        no_next = False
        no_prev = False
        if last >= len(values):
            values = values[first:]
            no_next = True
        else:
            values = values[first:last]

        if first <= 0:
            no_prev = True

        links = dict()
        if not no_prev:
            links[self.pagination_prev] = {self.pagination_pk_query_arg: original_page - 1,
                                           self.pagination_count_query_arg: pagination_count}
        if not no_next:
            links[self.pagination_next] = {self.pagination_pk_query_arg: original_page + 1,
                                           self.pagination_count_query_arg: pagination_count}

        return values, {'links': links}

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

    @classmethod
    def get_field_type(cls, name):
        super(InMemoryManager, cls).get_field_type(name)
        return BaseField(name)

    def delete(self, lookup_keys, *args, **kwargs):
        super(InMemoryManager, self).delete(lookup_keys, *args, **kwargs)
        if 'id' not in lookup_keys or not lookup_keys['id'] in self.queryset:
            raise NotFoundException('Blah...')
        self.queryset.pop(lookup_keys['id'])
        return None

    def _get_model(self, model_id):
        obj = self.queryset.get(model_id['id'], None)
        if not obj:
            raise NotFoundException('Blah...')
        return obj


class PersonInMemoryManager(InMemoryManager):
    model = 'Something'
    _model_name = 'Person'