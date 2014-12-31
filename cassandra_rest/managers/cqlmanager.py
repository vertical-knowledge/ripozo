__author__ = 'Tim Martin'
from cassandra_rest.managers.base import BaseManager, NotFoundException
from cqlengine.query import DoesNotExist
import logging


class CQLManager(BaseManager):
    """
    Works with serializing the models as json and deserializing them to cqlengine models
    """
    fail_create_if_exists = True
    allow_filtering = False

    def __init__(self):
        """

        :param viewset: The viewset that is using this serializer
        :type viewset: cassandra_rest.viewsets.base.APIBase
        """
        if self.model is None:
            raise ValueError('The model class attribute must be set: {0}'.format(self.__class__.__name__))
        if not self.fields or not isinstance(self.fields, (list, tuple,)):
            raise ValueError('the fields class attribute must be a list or tuple: '.format(self.__class__.__name__))
        self.initialize_args()
        super(CQLManager, self).__init__()

    def get_field_type(self, name):
        col = self.model._columns[name]
        return col.db_type

    @property
    def model_name(self):
        return self.model.__name__

    @property
    def queryset(self):
        return self.model.objects.all()

    def create(self, values, *args, **kwargs):
        """
        Creates an object using the specified values in the dict

        :param values: A dictionary with the attribute names as keys and the attribute values as values
        :type values: dict
        :return: Cassandra model object
        :rtype: cqlengine.Model
        """
        logger = logging.getLogger(__name__)
        logger.info('Creating model of type {0}'.format(str(self.model)))
        values = self._convert_multidict_to_dict(values)
        if self.fail_create_if_exists:
            obj = self.model.objects.if_not_exists().create(**values)
        else:
            obj = self.model.objects.create(**values)
        return self.serialize_model(obj)

    def retrieve(self, lookup_keys, *args, **kwargs):
        """
        Retrieves an existing object using the lookupkeys

        :param lookup_keys: A dictionary with the attribute names as keys and the attribute values as values
        :type lookup_keys: dict
        :return: The specified model using the lookup keys
        :rtype: dict
        """
        logger = logging.getLogger(__name__)
        logger.info('Retrieving model of type {0}'.format(str(self.model)))
        obj = self._get_model(lookup_keys)
        return self.serialize_model(obj)

    def retrieve_list(self, filters, *args, **kwargs):
        """
        Retrieves a list of all models that match the specified filters

        :param filters: The named parameters to filter the models on
        :type filters: dict
        :return: tuple 0 index = a list of the models as dictionary objects
        1 index = the query args for retrieving the next in pagination
        :rtype: list
        """
        logger = logging.getLogger(__name__)
        logger.info('Retrieving list of models of type {0} with filters: {1}'.format(str(self.model), filters))
        obj_list = []
        models = self.queryset
        if self.allow_filtering:
            logger.debug('Allowing filtering on list retrieval')
            models = models.allow_filtering()

        pagination_count, filters = self.get_pagination_count(filters)
        last_pagination_pk, filters = self.get_pagination_pks(filters)
        if not last_pagination_pk:
            last_pagination_pk = []

        if filters is not None:
            for key, value in filters.iteritems():
                models = models.filter(getattr(self.model, key) == value)
        if self.order_by is not None:
            models = models.order_by(self.order_by)

        models = self.pagination_filtration(models, last_pagination_pk=last_pagination_pk, filters=filters)
        models = models.limit(pagination_count + 1)

        last_model = None
        if len(models) > pagination_count:  # Handle the extra model used for finding the next batch
            last_model = models[-1]
            models = models[:pagination_count]

        for obj in models:
            obj_list.append(self.serialize_model(obj))
        if not pagination_count or not last_model:
            return obj_list, {self.pagination_pk_query_arg: None,
                              self.pagination_count_query_arg: pagination_count,
                              self.pagination_next: None}
        else:
            query_args, pagination_keys = self.get_next_query_args(last_model, pagination_count, filters=filters)
            return obj_list, {self.pagination_pk_query_arg: pagination_keys,
                              self.pagination_count_query_arg: pagination_count,
                              self.pagination_next: query_args}

    def update(self, lookup_keys, updates, *args, **kwargs):
        """
        Updates the model specified by the lookup_key with the specified updates

        :param lookup_keys:
        :type lookup_keys: dict
        :param updates:
        :type updates: dict
        :return:
        :rtype: cqlengine.Model
        """
        logger = logging.getLogger(__name__)
        logger.info('Updating model of type {0}'.format(str(self.model)))
        obj = self._get_model(lookup_keys)
        updates = self._convert_multidict_to_dict(updates)
        for key, value in updates.iteritems():
            col = self.model._get_column(key)
            if col.is_primary_key is True:
                continue
            setattr(obj, key, value)
        obj.save()
        return self.serialize_model(obj)

    def delete(self, lookup_keys, *args, **kwargs):
        """
        Deletes the model specified by the lookup_keys

        :param lookup_keys: A dictionary of fields and values on model to filter by
        :type lookup_keys: dict
        """
        logger = logging.getLogger(__name__)
        logger.info('Deleting model of type {0}'.format(str(self.model)))
        obj = self._get_model(lookup_keys)
        obj.delete()
        return

    def _convert_multidict_to_dict(self, values):
        """
        Converts werkzeurg multidict which contains lists to a standard dictionary
        """
        toreturn = {}
        for key, value in values.iteritems():
            if isinstance(value, list) and self.model._columns[key].db_type != 'list':
                toreturn[key] = value[0]
            else:
                toreturn[key] = value
        return toreturn

    def _get_model(self, lookup_keys):
        """
        Gets the model specified by the lookupkeys

        :param lookup_keys: A dictionary of fields and values on the model to filter by
        :type lookup_keys: dict
        """
        q = self.queryset
        for key, value in lookup_keys.iteritems():
            q = q.filter(getattr(self.model, key) == value)
        try:
            obj = q.get()
            return obj
        except DoesNotExist:
            raise NotFoundException('The model {0} could not be found.  '
                                    'lookup_keys: {1}'.format(self.model_name, lookup_keys))

    def get_next_query_args(self, last_model, pagination_count, filters=None):
        if last_model is None:
            return None, None
        query_args = '{0}={1}'.format(self.pagination_count_query_arg, pagination_count)

        for filter_name, filter_value in filters.iteritems():
            query_args = '{0}&{1}={2}'.format(query_args, filter_name, filter_value)
        pagination_keys = []
        for p_name in last_model._primary_keys:
            value = getattr(last_model, p_name)
            query_args = '{0}&{1}={2}'.format(query_args, self.pagination_pk_query_arg, value)
            pagination_keys.append(value)
        return query_args, pagination_keys

    def pagination_filtration(self, queryset, last_pagination_pk=None, filters=None):
        if filters is None:
            return queryset
        if last_pagination_pk is None:
            last_pagination_pk = []
        if len(last_pagination_pk) == 0:
            return queryset
        partition_key_count = len(self.model._partition_keys)
        for i in range(len(self.model._partition_keys)):
            key = self.model._partition_keys.items()[i][0]
            if key in filters:
                continue
            value = last_pagination_pk[i]
            queryset = queryset.filter(**{'{0}__gte'.format(key): value})
        if len(self.model._primary_keys) <= partition_key_count:
            return queryset

        clustering_pagination = last_pagination_pk[partition_key_count:]
        for i in range(len(clustering_pagination)):
            key = self.model._clustering_keys.items()[i][0]
            if key in filters:
                continue
            value = clustering_pagination[i]
            queryset = queryset.filter(getattr(self.model, key) >= value)
        return queryset

    def serialize_model(self, obj):
        """
        Takes a cqlengine.Model and jsonifies it.

        :param obj: The model instance to jsonify
        :type obj: cqlengine.Model
        :return: python dictionary with field names and values
        :rtype: dict
        """
        values = []
        for f in self.fields:
            values.append(getattr(obj, f))
        return self.serialize_fields(self.fields, values)