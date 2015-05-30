Flask Tutorial 1: Setting up the app
====================================

In this tutorial we will create a simple
message board application.  We will be using,
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

    pip install flask-ripozo, ripozo-sqlalchemy, Flask-User, Flask-SQLAlchemy

Next we'll need to create our application.

.. code-block:: python

    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config['SQLACLEHMY_DATABASE_URI']] = 'sqlite:////tmp/ripozo_example.db'
    db = SQLAlchemy(app)

Then we will setup our models.

.. code-block:: python

    from flask.ext.user import UserMixin
    from sqlalchemy.orm import relationship

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False, server_default='')
        reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
        email = db.Column(db.String(255), nullable=False, unique=True)
        confirmed_at = db.Column(db.DateTime())
        posts = relationship('Post', backref='user')
        comments = relationship('Comment', backref='user')

    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True):
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        post = db.Column(db.Text, nullable=False)

    class Comment(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        comment = db.Column(db.Text, nullable=False)

Now that we have our 
