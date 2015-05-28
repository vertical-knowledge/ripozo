from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import Flask

from flask_ripozo import FlaskDispatcher

from ripozo import apimethod, adapters
from ripozo import restmixins

from ripozo_sqlalchemy import AlchemyManager

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

import json

app = Flask(__name__)
app.debug = True

dispatcher = FlaskDispatcher(app)

Base = declarative_base()

class HelloModel(Base):
    __tablename__ = 'hello_model'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String(length=50))

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
session = Session(engine)


# Create the manager for the model
class HelloManager(AlchemyManager):
    _fields = ('id', 'value')
    _create_fields = ('value',)
    model = HelloModel
    session = session


class MyResource(restmixins.CreateRetrieveUpdateDelete):
    _pks = ('id',)
    _resource_name = 'resource'
    _manager = HelloManager

dispatcher.register_resources(MyResource)
dispatcher.register_adapters(adapters.SirenAdapter, adapters.HalAdapter)


if __name__ == '__main__':
    test_client = app.test_client()

    resp = test_client.post('/resource/', data=dict(value='hello world'))
    create_data = json.loads(resp.data)
    print(json.dumps(create_data, sort_keys=True, indent=4, separators=(',', ': ')))

    # We could also get this from the links in the SIREN protocol.
    url = '/resource/{0}/'.format(create_data['properties']['id'])

    # Lets give HAL a shot.
    retrieve_response = test_client.get(url, headers={'Content-Type': 'application/hal+json'})
    hal_retrieve_data = json.loads(retrieve_response.data)
    print(json.dumps(hal_retrieve_data, sort_keys=True, indent=4, separators=(',', ': ')))

    # Or SIREN explicitly.
    retrieve_response = test_client.get(url, headers={'Content-Type': 'application/vnd.siren+json'})
    siren_retrieve_data = json.loads(retrieve_response.data)
    print(json.dumps(siren_retrieve_data, sort_keys=True, indent=4, separators=(',', ': ')))

    print(siren_retrieve_data['properties']['value'])

    # Let's update it.
    update_response = test_client.patch(url, data=dict(value='goodbye'))
    update_data = json.loads(update_response.data)
    print(update_data['properties']['value'])

    # And finally delete it.
    delete_response = test_client.delete(url)
    print(delete_response.status_code)



