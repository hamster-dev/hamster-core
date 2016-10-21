from pipeline.pipeline import state_aware_task

@state_aware_task
def a_pull(pr):
    """A task with an arg having the same name as the event data
    """
    return pr

@state_aware_task
def another_pull(pullreq):
    """A task that has to have its name mapped
    """
    return pullreq
