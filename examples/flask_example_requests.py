from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from pypermedia.client import HypermediaClient
import requests


if __name__ == '__main__':
    siren_client = HypermediaClient.connect('http://127.0.0.1:5000/api/taskboard/')
    task_board_list = siren_client.retrieve_list()
    task_board_list.create(title='My First Board')
    resp = requests.post('http://127.0.0.1:5000/api/taskboard/', json=dict(title='My First Board'))
    print(resp.content)
    content = json.loads(resp.content)


