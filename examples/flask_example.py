from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_ripozo import FlaskDispatcher
from ripozo import restmixins, ListRelationship, Relationship, adapters, apimethod
from ripozo_sqlalchemy import AlchemyManager
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/ripozo_example.db'
db = SQLAlchemy(app)


class TaskBoard(db.Model):
    __tablename__ = 'task_board'
    id = db.Column(db.Integer, primary_key=True)
    tasks = relationship('Task', backref='task_board')
    title = db.Column(db.String(50), nullable=False)

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    task_board_id = db.Column(db.Integer, db.ForeignKey('task_board.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)

db.create_all()

class TaskBoardManager(AlchemyManager):
    _fields = ('id', 'title', 'tasks.id',)
    _list_fields = ('id', 'title',)
    _update_fields = ('title',)
    model = TaskBoard
    session = db.session
    paginate_by = 10

class TaskManager(AlchemyManager):
    _fields = ('id', 'task_board_id', 'title', 'description', 'completed',)
    model = Task
    session = db.session
    paginate_by = 20


class TaskBoardResource(restmixins.CreateRetrieveRetrieveListUpdateDelete):
    _manager = TaskBoardManager
    _resource_name = 'taskboard'
    _indv_name = 'taskboard'
    _pks = ('id',)
    _relationships = (
        ListRelationship('tasks', relation='TaskResource'),
    )

    @apimethod(route='/addtask', methods=['POST'])
    def add_task(cls, request):
        body_args = request.body_args
        body_args['task_board_id'] = request.get('id')
        request.body_args = body_args
        return TaskResource.create(request)

class TaskResource(restmixins.CreateRetrieveUpdateDelete):
    _manager = TaskManager
    _resource_name = 'task'
    _pks = ('id',)
    _relationships = [
        Relationship('task_board', property_map=dict(task_board_id='id'), relation='TaskBoardResource')
    ]

dispatcher = FlaskDispatcher(app, url_prefix='/api')
dispatcher.register_resources(TaskBoardResource, TaskResource)
dispatcher.register_adapters(adapters.SirenAdapter, adapters.HalAdapter)

if __name__ == '__main__':
    app.run(debug=True)
