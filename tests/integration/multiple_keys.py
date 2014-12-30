__author__ = 'Tim Martin'
from tests.base import FakeAppBase
from tests.integration.apitests import generate_random_name
from uuid import uuid1
import json


class TestMultipleKeys(FakeAppBase):
    def test_pagination(self):
        id1 = uuid1()
        id2 = uuid1()
        for i in range(50):
            if i % 10 == 0:
                id2 = uuid1()
            self.app.post('/api/multiple_keys',
                          data=dict(id1=id1, id2=id2),
                          follow_redirects=True)

        next_url = '/api/multiple_keys'
        while next_url is not None:
            response = self.app.get(next_url)
            data = json.loads(response.data)
            next_url = data.get('meta', {}).get('next')
            if next_url is not None:
                self.assertEqual(len(data.get('multiple_keys')), 5)