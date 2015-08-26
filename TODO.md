##TODO

###Tests
    - anonymize the webhook fixtures
    - fix integration tests with VCR/betamax, currently there is some weirdness.
        - note: check out github3.py's conftest.py, it uses betamax for fixtures
    - Figure out how to get tasks registered inside the tests for a django app.
    For now, I can only use tests that are part of the system already.
    The issue is that i cant get  the celery worker to run insude the
    app's tests directory.  It has to run outside, in hamster itself.
    
    
###Deployment:
    - When docker-compose 1.3 comes out, it supports custom dockerfiles
    - modify docker-compose.yml to use a non-dockerized postgres instance,
    so there is no risk of losing data between builds
    - mount app volume in dockerfile, instead of docker-compose.yml;
    this is just easier to understand
    - fix github host key veirification in worker.sh
    
    
###Cleanup
    - readme to md

###Events
    - suppost only one event per input, where the most specific event matches.
    this would likely be the lowest-level subclass
    
###General
    - fix proxy handling
    - create special property for events.  they shouldnt need to define both 
    properties and `data`, since `data` should expose ony those properties
    - Better logging for event handling (info about each event)
    

###Ideas
    - move config to yaml, similar to ansible?
    - can i get rid of 'self' in the actions?
    - allow variables to be defined by the user in the configuration,
    outside of any tasks. this should be easy, just pass them to the executor
    - refactor task action.  the idea is: the only real difference between task action
    and celery task is in the runtime error handling behavior.  celery errors are
    "unhandled exception, coudlnt execute the task", and these exceptions or the
    celery semipredicates affect the behavior of the rest of the tasks, like
    whether or not they are executed (like in a chain).  The only difference we have
    is that we want to use task return value (True or False, 0 or 1) to drive this
    behavior.  If we refactor to be a wrapper around task with these new behaviors,
    it will be more useful. Then I cna build the pipeline abstraction on top of THAT,
    so the two abstractions (task return behavior, and task pipeline) are completely
    separate. As of now they are completely mixed.
    