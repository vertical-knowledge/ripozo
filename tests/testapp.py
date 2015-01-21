__author__ = 'Tim Martin'
from flask import Flask
from tests.integration.helpers.viewsets import PersonViewset, DummyViewset, PaginatedPersonViewset, MultipleKeysViewset
from rest.viewsets.base import register_viewset

app = Flask(__name__)
register_viewset(app, PersonViewset)
register_viewset(app, DummyViewset)
register_viewset(app, PaginatedPersonViewset)
register_viewset(app, MultipleKeysViewset)


if __name__ == '__main__':
    app.run()