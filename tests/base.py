__author__ = 'Tim Martin'
import unittest
import testapp
from cqlengine import connection, QUORUM
from cqlengine.management import create_keyspace, delete_keyspace, sync_table, drop_table
from test_models import Person, Comment, Dummy, MultipleKeys


class TestBase(unittest.TestCase):
    test_keyspace_name = 'flask_cassandra_rest_test'

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        connection.setup(['192.168.56.102', '192.168.56.103'], cls.test_keyspace_name, QUORUM)
        create_keyspace(cls.test_keyspace_name, replication_factor=1)

    @classmethod
    def tearDownClass(cls):
        delete_keyspace(cls.test_keyspace_name)
        super(TestBase, cls).tearDownClass()


class DummyModelsBase(TestBase):

    @classmethod
    def setUpClass(cls):
        super(DummyModelsBase, cls).setUpClass()
        sync_table(Person)
        sync_table(Comment)
        sync_table(Dummy)
        sync_table(MultipleKeys)

    @classmethod
    def tearDownClass(cls):
        drop_table(Person)
        drop_table(Comment)
        drop_table(Dummy)
        drop_table(MultipleKeys)
        super(DummyModelsBase, cls).tearDownClass()


class FakeAppBase(DummyModelsBase):
    app = None

    @classmethod
    def setUpClass(cls):
        super(FakeAppBase, cls).setUpClass()
        testapp.app.config['TESTING'] = True
        cls.app = testapp.app.test_client()