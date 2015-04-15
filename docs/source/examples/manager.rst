Managers Example
================

This example assumes that ripozo-sqlalchemy is installed.
To install it simple

.. code-block:: bash

    pip install ripozo-sqlalchemy

.. code-block:: python

    from ripozo_sqlalchemy import AlchemyManager

    from sqlalchemy import Column, Integer, String, create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    # Setup the database with sqlalchemy
    Base = declarative_base(create_engine('sqlite:///:memory:', echo=True))
    session = sessionmaker()()

    # Declare your ORM model
    class Person(Base):
        __tablename__ = 'person'
        id = Column(Integer, primary_key=True)
        first_name = Column(String)
        last_name = Column(String)
        secret = Column(String)

       Base.metadata.create_all()



.. code-block:: python

    from ripozo_sqlalchemy import AlchemyManager

    class PersonManager(AlchemyManager):
        fields = ['id', 'first_name', 'last_name']
        model = Person
        paginate_by = 10
        sessions = session


.. code-block:: python

    from ripozo.viewsets.restmixins import CreateRetrieveList, RetrieveUpdateDelete
    from ripozo.viewsets.relationships import Relationship, ListRelationship

    class PersonListResource(CreateRetrieveList):
        _resource_name = 'people'
        _manager = PersonManager
        _namespace = '/api'
        _relationships = [
            ListRelationship('people', relation='PersonResource'),
        ],
        _links = [
            Relationship('created', relation='PersonResource'),
            Relationship('next', relation='PersonListResource'),
            Relationship('previous', relation='PersonListResource')
        ]

    class PersonResource(RetrieveUpdateDelete):
        _resource_name = 'person'
        _manager = PersonManager
        _pks = ['id']
        _namespace = '/api'