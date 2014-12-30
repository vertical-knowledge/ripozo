__author__ = 'Tim Martin'
from cqlengine.management import create_keyspace, delete_keyspace, sync_table, drop_table
from cqlengine import connection, ALL
import testapp
from test_models import CustomMethodModel
import unittest
import json
from cqlengine.exceptions import ValidationError


class TestCustomRoutes(unittest.TestCase):
    connection.setup(['192.168.56.103'], 'cassandra_serializer', ALL)

    def setUp(self):
        self.tearDown()
        create_keyspace('test_cassandra_serializer', replication_factor=1)
        testapp.app.config['TESTING'] = True
        self.app = testapp.app.test_client()
        sync_table(CustomMethodModel)

    def tearDown(self):
        drop_table(CustomMethodModel)
        delete_keyspace('cassandra_serializer')

    def test_standard_crud_routes(self):
        response = self.app.post('/test', data={'text': 'some text'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        model_id = data['id']
        response = self.app.get('/test')
        self.assertEqual(response.status_code, 200)
        response = self.app.get('/test/{0}'.format(model_id))
        self.assertEqual(response.status_code, 200)
        response = self.app.put('/test/{0}'.format(model_id), data={'text': 'other text'})
        self.assertEqual(response.status_code, 200)
        response = self.app.delete('/test/{0}'.format(model_id))
        self.assertEqual(response.status_code, 204)

    def test_other_route(self):
        response = self.app.get('/test/other_route')
        self.assertEqual('Other route', response.data)
        response = self.app.post('/test/other_route')
        self.assertEqual('Other route', response.data)

    def test_begging_slash(self):
        response = self.app.get('/test/beginning_slash')
        self.assertEqual('Another route', response.data)

    def test_multiple_routes(self):
        response = self.app.get('/test/route1')
        self.assertEqual('Multiple routes', response.data)
        response2 = self.app.get('/test/route2')
        self.assertEqual('Multiple routes', response2.data)
        self.assertEqual(response.data, response2.data)

    def test_patch_route(self):
        response = self.app.patch('/test/patch')
        self.assertEqual('Patch route', response.data)

    def test_non_existing_route(self):
        self.assertRaises(ValidationError, self.app.get, '/test/doesnt_exist')