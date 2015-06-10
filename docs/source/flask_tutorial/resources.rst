Resources
=========

Resources are the core of ripozo.  These are common
across all manager and dispatcher packages.  This means,
assuming that the application was developed well, you could
reuse the resources in Django or mix them in with the cassandra
manager.

.. code-block:: python

    from ripozo import restmixins, ListRelationship, Relationship


    class TaskBoardResource(restmixins.CreateRetrieveRetrieveListUpdateDelete):
        manager = TaskBoardManager(session_handler)
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
        manager = TaskManager(session_handler)
        _resource_name = 'task'
        _pks = ('id',)
        _relationships = (
            Relationship('task_board', property_map=dict(task_board_id='id'), relation='TaskBoardResource'),
        )

 Now we have a completely reusable basis for our RESTful application!
