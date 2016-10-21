from core.pipeline import (
    Pipeline,
    Task,
    TaskArgument, 
    LazyTaskArgument, 
    TemplateTaskArgument
)


def test_task():
    """Test that a task is created successfully.
    """
    task = Task(
         'echo',
         [TaskArgument('arg', 'sometext')]
        )
    assert task.task_name == 'echo'
    assert len(task.arguments) == 1
    assert task.arguments['arg'] == 'sometext'


def test_task_argument():
    """Test that a TaskArgument is correctly sent to pipeline."""
    event_data = {'lastname': 'waters'}

    task = Task(
         'echo',
         [TaskArgument('arg', 'sometext')]
        )

    pipeline = Pipeline([task])

    ret = pipeline.run(event_data).get()

    # pipeline will return a `pipeline.state.StateTracker` instance
    assert ret.echo == 'sometext'


def test_lazy_task_argument():
    """Test that a LazyTaskArgument is correctly sent to pipeline."""
    event_data = {'lastname': 'waters'}

    tasks = [
            Task(
                'echo',
                [
                 TaskArgument('arg', 'blarg'),
                ]
            ),
            Task(
                'echo_again',
                [
                 LazyTaskArgument('arg', 'echo')
                ]
            )
        ]
    pipeline = Pipeline(tasks)

    ret = pipeline.run(event_data).get()


    ret = pipeline.run(event_data).get()

    # pipeline will return a `pipeline.state.StateTracker` instance
    assert ret.echo_again == 'blarg'


def test_lazy_template_argument():
    """Test that a LazyTemplate is correctly sent to pipeline."""
    event_data = {'lastname': 'waters'}

    tasks = [
            Task(
                'echo',
                [
                 TaskArgument('arg', 'blarg'),
                ]
            ),
            Task(
                'echo_again',
                [
                 TemplateTaskArgument('arg', 'hello {{ echo }}')
                ]
            )
        ]
    pipeline = Pipeline(tasks)

    ret = pipeline.run(event_data).get()


    ret = pipeline.run(event_data).get()
    # pipeline will return a `pipeline.state.StateTracker` instance
    assert ret.echo_again == 'hello blarg'
