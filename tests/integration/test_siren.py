__author__ = 'Tim Martin'
from cqlengine.management import create_keyspace, delete_keyspace, sync_table, drop_table
from cqlengine import connection, ALL
import testapp
from testapp import SomethingElse
import unittest
import json
from cqlengine.exceptions import ValidationError


class TestSiren(unittest.TestCase):
    connection.setup(['192.168.56.103'], 'cassandra_serializer', ALL)

    def setUp(self):
        self.tearDown()
        create_keyspace('test_cassandra_serializer', replication_factor=1)
        testapp.app.config['TESTING'] = True
        self.app = testapp.app.test_client()
        sync_table(SomethingElse)

    def tearDown(self):
        drop_table(SomethingElse)
        delete_keyspace('cassandra_serializer')

    def test_siren_get(self):
        response = self.app.get('/siren')
        data = json.loads(response.data)
        x = 10