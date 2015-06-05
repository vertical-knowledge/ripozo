Resources
=========

Resources are the core of ripozo.  These are common
across all manager and dispatcher packages.  This means,
assuming that the application was developed well, you could
reuse the resources in Django or mix them in with the cassandra
manager.

.. code-block:: python

    from ripozo import restmixins, ListRelationship, Relationship

    class TaskBoardResourceList(restmixins.RetrieveRetrieveList):
        _manager = TaskBoardManager
        _resource_name = 'taskboard'
        _relationships = [
            ListRelationship('taskboard', relation='TaskBoardResource')
        ]

    class TaskBoardResource(restmixins.CreateRetrieveUpdateDelete):
        _manager = TaskBoardManager
        _resource_name = 'taskboard'
        _pks = ('id',)
        _relationships = [
            ListRelationship('tasks', relation='TaskResource')
        ]

    class TaskResource(restmixins.CreateRetrieveUpdateDelete):
        _manager = TaskManager
        _resource_name = 'task'
        _pks = ('id',)
        _relationships = [
            Relationship('task_board', relation='TaskBoardResource')
        ]

 Now we have a completely reusable basis for our RESTful application!
