__author__ = 'Tim Martin'
from abc import ABCMeta, abstractmethod, abstractproperty
from rest.utilities import make_json_serializable, convert_to_datetime, convert_to_boolean
from decimal import Decimal
from webargs import Arg
import logging


class NotFoundException(Exception):
    pass


class BaseManager(object):
    """
    The BaseManager implements some common methods that are valuable across all databases
    as well as expose an interface that must be implemented by any specific implementation.
    This needs to be extended in order to implement a new database type.  This should handle
    all direct interactions with a database or ORM.  The extended classes are injected into
    viewsets in order to specify how to get the data from the database.

    :param pagination_pk_query_arg: The name of the query parameter that specifies the page or pk
    for the next set page to return when paginating over a list
    :type pagination_pk_query_arg: str
    :param pagination_count_query_arg: The name of the query parameter that specifies the maximum number of results
    to return in a list retrieval
    :type pagination_count_query_arg: str
    :param pagination_next: The meta parameter to return that specifies the next query parameters
    :type pagination_next: str
    :param paginate_by: The number of results to return by default.  This gets overridden by pagination_count_query_arg
    :type paginate_by: int
    :param order_by: A list of the fields to order the results by.  This may be restricted in certain databases
    :type order_by: list
    :param fields: A list of the fields that are able to be manipulated or retrieved by the _manager
    :type fields: list
    :param model: The model that is being managed.  This is the individual model that is set by the user.
    For any type of base class this should be None.  However, it is required for actual implementations
    :type model: type
    """
    __metaclass__ = ABCMeta
    pagination_pk_query_arg = 'pagination_pk'
    pagination_count_query_arg = 'count'
    pagination_next = 'next'
    paginate_by = 10000
    order_by = None
    fields = None
    model = None
    arg_parser = None

    @abstractmethod
    def create(self, values, *args, **kwargs):
        """
        Create a model with the values according to the values dictionary

        :param values: A dictionary of values to create the model according to
        :type values: dict
        :param args: Extra arguments
        :type args: tuple
        :param kwargs: Extra keyword arguments
        :type kwargs: dict
        :return: The dictionary of arguments that should be returned by the serializer
        :rtype: dict
        """
        pass

    @abstractmethod
    def retrieve(self, lookup_keys, *args, **kwargs):
        """
        Retrieve a single model and nothing more as a python dictionary

        :param lookup_keys: The lookup keys for the model and the associated values
        :type lookup_keys: dict
        :param args: Extra arguments
        :type args: tuple
        :param kwargs: Extra keyword arguments
        :type kwargs: dict
        :return: The dictionary of arguments that should be returned by the serializer
        :return: A tuple with the first object being a dictionary of key value pairs according to the fields list and
        the second object is the meta data (such as the next url for a paginated list)
        :rtype: tuple
        """
        pass

    @abstractmethod
    def retrieve_list(self, filters, *args, **kwargs):
        """
        Retrieves a list of dictionaries containing the fields for the associated model

        :param lookup_keys: The lookup keys for the model and the associated values
        :type lookup_keys: dict
        :param args: Extra arguments
        :type args: tuple
        :param kwargs: Extra keyword arguments
        :type kwargs: dict
        :return: The dictionary of arguments that should be returned by the serializer
        :return: A a list of dictionaries of key value pairs according to the fields list
        :rtype: list
        """
        pass

    @abstractmethod
    def update(self, lookup_keys, updates, *args, **kwargs):
        """
        Updates the model found with the lookup keys according to the updates dictionary where
        the keys are the fields to update and the values are the new values for the field

        :param lookup_keys: The keys to find the object that is to be updated
        :type lookup_keys: dict
        :param updates: The fields to update and their associated new update values
        :type updates: dict
        :param args: Extra arguments
        :type args: tuple
        :param kwargs: Extra keyword arguments
        :type kwargs: dict
        :return: A dictionary of the full updated model according to the fields class attribute
        :rtype: dict
        """
        pass

    @abstractmethod
    def delete(self, lookup_keys, *args, **kwargs):
        """
        Deletes the model found with the lookup keys

        :param lookup_keys: The keys with which to find the model to delete
        :type lookup_keys: dict
        :param args: Extra arguments
        :type args: tuple
        :param kwargs: Extra keyword arguments
        :type kwargs: dict
        :return: nothing.
        :rtype: NoneType
        """
        pass

    @abstractmethod
    def get_field_type(self, name):
        """
        This should return the field type for the given name.  This is used to construct
        the webargs parser

        :param name: The name of the field on the mode for which you are getting the field name
        :type name: str
        :return: The type of the field
        :rtype: type
        """
        pass

    @abstractproperty
    def model_name(self):
        """
        Get the name of the model being represented.  The individual model instance is irrelevant.
        For example if you had a Person model, it might return "person"

        :return: name of the model
        :rtype: unicode
        """
        pass

    @abstractproperty
    def queryset(self):
        """
        Gets the list of models that are valid to operate on

        :return: A list of models
        :rtype: list
        """
        pass

    def get_pagination_count(self, filters):
        """
        Get the pagination count from the args

        :param filters: All of the args
        :type filters: dict
        :return: tuple of (pagination_count, updated_filters
        :rtype: tuple
        """
        # get the pagination count or else use the default
        logger = logging.getLogger(__name__)
        filters = filters.copy()
        pagination_count_query = filters.pop(self.pagination_count_query_arg, None)
        pagination_count = int(pagination_count_query) if pagination_count_query else self.paginate_by
        logger.debug('Paginating list by {0}'.format(pagination_count))
        return pagination_count, filters

    def get_pagination_pks(self, filters):
        """
        Get the pagination pks from the args

        :param filters: All of the args
        :type filters: dict
        :return: tuple of (pagination_pks, updated_filters
        :rtype: tuple
        """
        filters = filters.copy()
        last_pagination_pk = filters.pop(self.pagination_pk_query_arg, None)
        return last_pagination_pk, filters

    def initialize_args(self):
        """
        Sets up the webargs parser so that it can read and effectively type incoming request variables

        :return: Nothing
        :rtype: NoneType
        """
        self.arg_parser = dict()

        # set up the pagination args
        self.arg_parser[self.pagination_pk_query_arg] = Arg(str, multiple=True, allow_missing=True)
        self.arg_parser[self.pagination_count_query_arg] = Arg(int, multiple=False, allow_missing=True)

        # only allow the specified fields
        for name in self.fields:
            t = self.get_field_type(name)
            multiple = False
            use = None
            # Get the correct type to cast the incoming argument to
            if t in ['text', 'ascii', 'uuid', 'timeuuid']:
                arg_type = str
            elif t in ['int', 'varint']:
                arg_type = int
            elif t == 'bigint':
                arg_type = long
            elif t == 'timestamp':
                arg_type = convert_to_datetime
            elif t == 'boolean':
                arg_type = bool
                use = convert_to_boolean
            elif t == 'double':
                arg_type = float
            elif t == 'decimal':
                arg_type = Decimal
            elif 'set<' in t:
                arg_type = set
                multiple = True
            elif 'list<' in t:
                arg_type = list
                multiple = True
            elif 'map<' in t:
                arg_type = dict
                multiple = True
            elif t == 'blob':
                arg_type = bytes
            else:
                raise TypeError('Unexpected column type: {0}'.format(t))

            self.arg_parser[name] = Arg(arg_type, multiple=multiple, use=use, allow_missing=True)

    @classmethod
    def serialize_fields(cls, field_names, field_values):
        """
        Takes two lists and iterates through them to combine them into a dictionary

        :param field_names: The names of the fields that were retrieved.  Order is important.
          These will be the dictionary keys
        :type field_names: list
        :param field_values: The values that were retrieved. These will be the dictionary values
        :type field_values: list
        :return: A dictionary of the combined lists
        :rtype: dict
        """
        dictified = {}
        for i in range(len(field_names)):
            dictified[field_names[i]] = make_json_serializable(field_values[i])
        return dictified