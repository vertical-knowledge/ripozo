__author__ = 'Tim Martin'
from cassandra_rest.managers.alcehmymanager import AlchemyManager
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from cassandra_rest.managers.base import NotFoundException
from tests.unit.managers.test_manager_base import TestManagerBase

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app=app)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))

db.create_all()


class PersonManager(AlchemyManager):
    db = db
    model = Person
    paginate_by = 10
    fields = ('id', 'first_name', 'last_name')


class TestAlchemyManager(TestManagerBase):
    @property
    def manager(self):
        return PersonManager()

    @property
    def all_person_models(self):
        return Person.query.all()

    def get_person_model_by_id(self, person_id):
        to_return = Person.query.get(person_id)
        if to_return is None:
            raise NotFoundException
        return to_return

    @property
    def does_not_exist_exception(self):
        return NotFoundException

    def test_get_field_type(self):
        manager = self.manager
        self.assertEqual(manager.get_field_type('first_name'), str)
        self.assertEqual(manager.get_field_type('last_name'), str)
        self.assertEqual(manager.get_field_type('id'), int)

    def test_retrieve_many_pagination_arbitrary_count(self):
        pass # arbitrary count doesn't really make sense