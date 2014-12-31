__author__ = 'Tim Martin'
from cassandra_rest.managers.base import BaseManager, NotFoundException


class AlchemyManager(BaseManager):
    db = None  # the database object needs to be given to the class
    pagination_pk_query_arg = 'page'

    def get_field_type(self, name):
        raise NotImplementedError

    def create(self, values, *args, **kwargs):
        model = self.model()
        for name, value in values.iteritems():
            setattr(model, name, value)
        self.db.session.add(model)
        self.db.session.commit()

    def retrieve(self, lookup_keys, *args, **kwargs):
        return self.serialize_model(self._get_model(lookup_keys))

    def retrieve_list(self, filters, *args, **kwargs):
        pagination_count, filters = self.get_pagination_count(filters)
        pagination_pk, filters = self.get_pagination_pks(filters)
        if isinstance(pagination_pk, (list, tuple)):
            if len(pagination_pk) == 0:
                pagination_pk = None
            else:
                pagination_pk = pagination_pk[0]

        if pagination_pk is None:
            pagination_pk = 1
        q = self.queryset.filter_by(**filters)
        q = q.paginate(pagination_pk, pagination_count, False)
        if self.order_by:
            q = q.order_by(self.order_by)
        model_list = []
        for m in q:
            model_list.append(self.serialize_model(m))
        next_page = pagination_pk + 1
        query_args = '{0}={1}&{2}={3}'.format(self.pagination_pk_query_arg, next_page,
                                              self.pagination_count_query_arg, pagination_count)
        return model_list, {self.pagination_pk_query_arg: next_page,
                            self.pagination_count_query_arg: pagination_count,
                            self.pagination_next: query_args}

    def update(self, lookup_keys, updates, *args, **kwargs):
        model = self._get_model(lookup_keys)
        for name, value in updates.iteritems():
            setattr(model, name, value)
        model.save()
        self.db.session.commit()
        return self.serialize_model(model)

    def delete(self, lookup_keys, *args, **kwargs):
        model = self._get_model(lookup_keys)
        self.db.session.delete(model)
        self.db.session.commit()

    @property
    def model_name(self):
        return self.model.__name__

    @property
    def queryset(self):
        return self.model.query.all()

    def _get_model(self, lookup_keys):
        """
        Gets the model specified by the lookupkeys

        :param lookup_keys: A dictionary of fields and values on the model to filter by
        :type lookup_keys: dict
        """
        row = self.queryset.get(lookup_keys.values())
        if row is None:
            raise NotFoundException('The model {0} could not be found. '
                                    'lookup_keys: {1}'.format(self.model_name, lookup_keys))
        return row

    def serialize_model(self, obj):
        values = []
        for f in self.fields:
            values.append(getattr(obj, f))
        return self.serialize_fields(self.fields, values)