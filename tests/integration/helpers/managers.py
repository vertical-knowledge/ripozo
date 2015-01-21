__author__ = 'Tim Martin'
from rest.managers.cqlmanager import CQLManager
from tests.test_models import Person, Dummy, MultipleKeys


class PersonManager(CQLManager):
    model = Person
    fields = ('id', 'first_name', 'last_name')


class DummyManager(CQLManager):
    model = Dummy
    fields = ('id', 'id2_', 'text_', 'boolean_', 'int_', 'long_', 'varint_', 'datetime_', 'bytes_',
              'ascii_', 'float_', 'decimal_', 'set_', 'list_', 'map_')


class PaginatedPersonManager(PersonManager):
    paginate_by = 2


class MultipleKeysManager(CQLManager):
    model = MultipleKeys
    fields = ('id1', 'id2', 'id3')
    paginate_by = 5
    allow_filtering = True