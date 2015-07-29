# Hamster CI
![Hamster](http://i5.glitter-graphics.org/pub/1933/1933385pgqm471nc2.jpg)

A distributed python3 system that reacts to github events, allowing a user to specify actions 
to be taken when these events occur.  Actions are executed on remote workers, using the 
`celery` library.

Hamster knows how to 
  - run shell commands
  - interact with github
  - execute developer-defined, runtime-configured python functions 

Actions are configured by the user in the UI and are saved into a database,
which is read by the appserver when a triggering event occurs, and then scheduled
to be executed on a worker.

Actions, while technically distributed across nodes, are (currently) executed
serially in a pipeline, using the `celery-pipeline` library.


# Technical overview

    Event --> EventHandler --> Actions

Input entering the system is deserialized to one or more `Event`s.
Events expose the deserialized input data as properties, which 
are carried forward through the rest of the system.

When an event occurs, the system is searched for matching `Event Handlers`,
which are created and stored by the end-user.  Event handlers store the
Actions which are to be performed, and these actions can access the data
stored in the Event (using jinja templates) in order to modify their behavior.

# Example

Here is a docs-friendly example of a simple event handler:

    name: Pull Request Linter
    events: pull_request.opened, pull_request.reopened
    criteria: source.repository is Hello-World
    actions:
      - shell_command
        name: 'linter'
        args:
          - 'pip install pylint && pylint ./'
      - pull_request_comment
        args:
          - 'hey @{{ source.user }} pylint returned {{ linter.output }}'
          
The above event handler would fire for the 'Hello-World' repo, when a pull
request is opened or reopened, and would run pylint on the checked out repo 
(more on this later), emitting a comment to the originating pull request with 
the output of the pylint command.

Note that not only is the event data available to the action (source.user), the 
result of previously-executed actions is available (linter.output).  This 
allows us to build powerful pipelines that can automate our github workflows.
          
## Checked-out repo
Defined source classes (like `PullRequest`) provide instructions to the system
for obtaining their on-disk representations. The system provides a Workspace, 
located on the disk on the worker, that an action can use; when used, it will 
obtain the source locally.  For a PullRequest, this means cloning the
repository and checking out the pull request branch.  Shell commands executed
in the workspace will be run inside the cloned repository directory.
The workspaces are temporary, and are deleted when the action is completed.


# Using Hamster
Hamster is packaged with all the code necessary for deployment inside Docker
containers.  
The application architecture includes:

  - celery worker/s
  - gunicorn app workers
  - nginx for static files and for proxying to gunicorn
  - redis as the broker (TODO: rabbitmq)
  - postgresql database

In order to get a running hamster, there are a few prerequisites.

## Prerequisites
### 1. Environment variables
Hamster requires some information, stored in environment variables.

Required variables are:

  - HAMSTER_GITHUB_API_TOKEN - a valid github API token
  - HAMSTER_GITHUB_API_USERNAME - username for above token
These variables are used for connectig to github via it's ReST API.

Optional supported variables are:

  - HAMSTER_GITHUB_HOST - hostname for a github enterprise instance, if used
  - NO_PROXY - proxy ignores if running behind corp proxy
  
### 2. Files
Hamster requires a keypair that can connect to github, in order to access
repositories using the git protocol, and therefore requires the following files:

  - github.key
  - github.pub
  
Place these files in the source root before deployment.

## Deployment
In order to deploy, simply run the following:

    docker-compose build
    docker-compose up -d
    
Use `docker-compose scale` to scale out your hamster when required.

Hamster provides a Makefile containing commonly used commands.
The `make scratch` command will install the system from nothing.


### Authentication
Upon deployment, one superuser is created for django admin: 

    hamster:hamster

### Deployment testing
A dev version of docker-compose.yml is provided.  Additionally, hamster
will install, into the docker container, any python modules found in the root 
directory during deployment, if $HAMSTER_DEBUG env var is set.

## Running locally
TODO does this work anymore?
If you wish to test hamster out without docker, you can.
You will need redis running, and two terminals (app/worker).
This will use sqlite as the database.

### Install

    VIRTUALENV_PYTHON=`which python3` mkvirtualenv hamster-ci
    workon hamster-ci
    pip install -r requirements.txt -r requirements-runtime.txt
    DJANGO_SETTINGS_MODULE=hamster.local_settings python hamster/manage.py migrate
    # below is an interactive command
    DJANGO_SETTINGS_MODULE=hamster.local_settings python hamster/manage.py createsuperuser
    
### Run
#### Web app

    cd hamster
    export PIPELINE_GITHUB_TOKEN=abcdefg123456
    export DJANGO_SETTINGS_MODULE=hamster.local_settings 
    gunicorn hamster.wsgi:application

#### Worker

    cd hamster
    export PIPELINE_GITHUB_TOKEN=abcdefg123456
    export DJANGO_SETTINGS_MODULE=hamster.local_settings 
    celery -A hamster worker -l debug
    

# Technical details
## Event
Input data is deserialized to one or more `Event`s.  An example
event is "pull request comment".  Each event type exposes some properties to the rest 
of the system; a mandatory `source`, which for the above example would be a 
`PullRequest`, and optional other event data, like an `IssueComment` containing
the body and author of the comment.

## Event handler
After input is deserialized and one or more events fire, the system
is searched for matching event handlers.  Event handlers are created by the
end-user and are stored in the database.  Each handler specifies the conditions
under which it is relevant, and the actions that should be executed when
those conditons are met. So, and event handler can specify that actions X and Y 
should be executed when a pull request is opened for repository Z.

## Actions
Actions are functions that internally are encapsulated in celery tasks.
Arguments stored in the event handler (and templated at runtime) are applied
to the functions and scheduled to be executed by a worker.

## Callbacks
When configuring event handlers, users can specify callbacks to be 
executed based on the return value of an action.  These callbacks are themselves 
actions.  Callbacks are typically used to provide a notification of the status
of an action, for instance emitting a pull request comment with the action's
output, or changing the commit status or the pull request's HEAD (this feature
is in progress).
me, with your changes.  You do need to reload for every change, though.