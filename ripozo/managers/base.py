from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty

from ripozo.decorators import classproperty

import logging
import six
logger = logging.getLogger(__name__)


@six.add_metaclass(ABCMeta)
class BaseManager(object):
    """
    The BaseManager implements some common methods that are valuable across all databases
    as well as expose an interface that must be implemented by any specific implementation.
    This needs to be extended in order to implement a new database type.  This should handle
    all direct interactions with a database or ORM.  The extended classes are injected into
    viewsets in order to specify how to get the data from the database.

    :param unicode pagination_pk_query_arg: The name of the query parameter
        that specifies the page or pk
        for the next set page to return when paginating over a list
    :param unicode pagination_count_query_arg: The name of the
        query parameter that specifies the maximum number of results
        to return in a list retrieval
    :param unicode pagination_next: The meta parameter to return that
        specifies the next query parameters
    :param int paginate_by: The number of results to return by default.
        This gets overridden by pagination_count_query_arg
    :param list order_by: A list of the fields to order the results by.
        This may be restricted in certain databases
    :param list _fields: A list of the fields that are able to be manipulated
        or retrieved by the manager.  These are the default fields if
        _create_fields, _list_fields, or _update_fields are not defined.
    :param list _create_fields: The fields to use if a model is being
        created.  Fields not in this list will not be applied
    :param list _list_fields: The fields to use if a list of models
        are being retrieved. If not defined, cls.fields will be used instead.
    :param list _update_fields: The fields to use if the model is
        being updated.  Fields not in this list will not be used.
    :param type model: The model that is being managed.
        This is the individual model that is set by the user.
        For any type of base class this should be None.
        However, it is required for actual implementations
    """
    pagination_pk_query_arg = 'pagination_pk'
    pagination_count_query_arg = 'count'
    pagination_next = 'next'
    pagination_prev = 'previous'
    paginate_by = 10000
    order_by = None
    _fields = None
    _create_fields = None
    _list_fields = None
    _update_fields = None
    model = None
    arg_parser = None
    _field_validators = None

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

    @classmethod
    def get_field_type(cls, name):
        """
        Returns the BaseField instance (or subclass) instance
        that corresponds to the named attribute on the model.
        For example, if you the column "name" on the model
        for this manager is a String column, then this should
        return an instance of StringField with the appropriate
        requirements.

        :param name: The name of the field on the model
            for which you are getting the field name
        :type name: unicode
        :return: The BaseField class (or subclass) instance to handle
            the field specified by the name
        :rtype: ripozo.viewsets.fields.base.BaseField
        """
        pass

    @classproperty
    def fields(cls):
        """
        Simply makes sure that the _fields attribute is not
        None.  Returns [] if cls._fields evaluates to None
        or some equivalent.
        """
        return cls._fields or []

    @classproperty
    def create_fields(cls):
        """
        These are the fields that are valid when
        creating a model.  This is necessary when you
        want the user to only be able to specify certain
        fields on creation.  Defaults to ``cls.fields``
        if ``cls._create_fields`` is not specified

        :return: The list of fields to use when creating
            a model using this manager
        :rtype: list
        """
        # TODO test this explicitly
        return cls._create_fields or cls.fields

    @classproperty
    def list_fields(cls):
        """
        These are the fields that should be used for
        retrieving a list of models.  This is often necessary
        for performance reasons when you only want the ids to
        create links to the individual resource and not the full
        resource

        :return: The list fields, if the ``cls._list_fields`` attribute is
            set, otherwise, ``cls.fields``
        :rtype: list
        """
        return cls._list_fields or cls.fields

    @classproperty
    def update_fields(cls):
        """
        These are the valid fields for updating a model.
        If the cls._update_fields is defined then it
        returns that list, otherwise it returns cls.fields

        :return: The list of fields to use when updating a model.
        :rtype: list
        """
        return cls._update_fields or cls.fields

    @classproperty
    def field_validators(cls):
        """
        Gets the BaseField instances for all of the
        fields on the manager.

        :return:
        :rtype: list
        """
        cls._field_validators = cls._field_validators or {}
        for field_name in cls.fields:
            if field_name not in cls._field_validators:
                cls._field_validators[field_name] = (cls.get_field_type(field_name))
        return list(cls._field_validators.values())

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

    def dot_field_list_to_dict(self, fields=None):
        """
        Converts a list of dot delimited fields (and related fields)
        and turns it into a dictionary for example, it would transform

        .. code-block:: python

            >>> dot_field_list_to_dict(['id', 'value', 'related.id', 'related.related_value'])
            {
                'id': None,
                'value': None,
                'related': {
                    'id': None,
                    'related_value': None
                }
            }

        :param list fields:
        :return: A dictionary of the fields layered as to
            indicate relationships.
        :rtype: dict
        """
        # TODO find a better fucking way
        field_dict = {}
        fields = fields or self.fields
        for f in fields:
            field_parts = f.split('.')
            current = field_dict
            part = field_parts.pop(0)
            while len(field_parts) > 0:
                current[part] = current.get(part, dict())
                current = current[part]
                part = field_parts.pop(0)
            current[part] = None
        return field_dict
