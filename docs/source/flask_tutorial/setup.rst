Flask Tutorial 1: Setting up the app
====================================

In this tutorial we will create a todo list
application.  We will be using,
flask-ripozo (Which include Flask of course), ripozo-sqlalchemy
(Which uses SQLAlchemy) and Flask-User for authentication.

The first step is to install the required dependencies.  I
highly recommend setting this up in a virtual environment of
course.

.. code-block:: bash

    pip install flask-ripozo, ripozo-sqlalchemy, Flask-User

Setting up the Flask application
--------------------------------

The first step is to install the required dependencies.  I
highly recommend setting this up in a virtual environment of
course.

.. code-block:: bash

    pip install flask-ripozo, ripozo-sqlalchemy, Flask-SQLAlchemy

Next we'll need to create our application.

.. code-block:: python

    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/ripozo_example.db'
    db = SQLAlchemy(app)

Then we will setup our models.

.. code-block:: python

    from sqlalchemy.orm import relationship

    class TaskBoard(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        tasks = relationship('Task', backref='task_board')
        title = db.Column(db.String(50), nullable=False)

    class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        task_board_id = db.Column(db.Integer, db.ForeignKey('task_board.id'), nullable=False)
        title = db.Column(db.String(50), nullable=False)
        description = db.Column(db.Text, nullable=False)
        completed = db.Column(db.Boolean, default=False)

    db.create_all()

Now that we have our non-ripozo aspect set up we
are ready to start building a RESTful API!
