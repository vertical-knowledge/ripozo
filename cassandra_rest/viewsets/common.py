__author__ = 'Tim Martin'
from cassandra_rest.utilities import convert_to_underscore
from restmixins import Create, RetrieveList, RetrieveSingle, Update, Delete
import re
import logging


class CreateRetrieveDeleteViewSet(Create, RetrieveSingle, RetrieveList, Delete):
    def get(self, **kwargs):
        for f in self.fields:
            if f not in kwargs:
                return self.retrieve_list()
        return self.retrieve()

    def post(self, **kwargs):
        return self.create()

    def delete(self, **kwargs):
        return self.remove(**kwargs)


class CRUD(Create, RetrieveList, RetrieveSingle, Update, Delete):
    """
    A standard create, retrieve, update and delete api class based viewset
    """

    def get(self, **kwargs):
        for f in self.pks:
            if f not in kwargs:
                return self.retrieve_list(**kwargs)
        return self.retrieve(**kwargs)

    def post(self, **kwargs):
        return self.create(**kwargs)

    def put(self, **kwargs):
        return self.update(**kwargs)

    def patch(self, **kwargs):
        return self.put(**kwargs)

    def delete(self, **kwargs):
        return self.remove(**kwargs)