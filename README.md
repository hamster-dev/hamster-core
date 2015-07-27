# Hamster CI
![Hamster](http://i5.glitter-graphics.org/pub/1933/1933385pgqm471nc2.jpg)

A system for building stuff.  

Built atop `pipeline`.



# Pipeline
`pipeline` is a django app to facilitate the execution of user-defined 
actions initialized by some event, and conditionally executed based on some 
predicate, .  IOW, the 'if this, then that' model.

Requires python3.4

## The Idea
Some event enters the system, and pipeline inspects it.  If it's a known event
type, the data provided by the event is serialized into a "source".
User-defined configuration db is then searched for a configuration that matches
the source instance; if a configuration is found, the user-defined actions
stored in that configuration are handed off to an executor which initializes 
and sends them to the celery scheduler to be executed by a worker.  Each
defined action supports success and failure handlers, which are also
executed by the celery scheduler based on the truthiness of the action's
return value.

The actions as a group are (currently) executed synchronously, in-order,
 using the ``celery.chain`` construct.
Each action is provided with the return value of the action preceeding it.

Sources can provide an on-disk representation, and pipeline supports
acquiring the source and storing it in a temporary workspace directory.
The workspace abstraction supports the execution of shell commands within
the context of that directory and a given system environment and user account.
If an action representing a shell command is executed, a workspace will
automatically be created and the source's files will be acquired and
stored in the workspace in order to support the shell command.

## Implementation
The event handling system is currently implemented using a Django view.

The only currently supported event hook method is 'push'. Possible future
event hooks are 'poll' and 'schedule'.  

### Design considerations
In order to implement a system with user defined inputs and outputs,
some measure of decoupling is required.  In a classical application, you 
might find liberal usage of interfaces to define how components are
allowed to interact with each other. Instead, pipeline (ab)uses duck 
typing; if an output component expects to operate on a PullRequest source object,
it should just assume that the source provided to it implements the same 
interface as that object (i.e. has a source_branch, an ssh_url etc.).

Additionally, pipeline makes use of the registry pattern for almost everything,
so that components don't have to know how to acquire each other (which
will almost certainly lead to cyclical import errors).  Each supported
component will define a 'friendly name' that other components can use to 
reference it.

## Currently supported inputs and outputs
Currently "pull request open" github webhook is the only implemented event 
type.  It is (de)serialized to a ``pipeline.modules.github.PullRequest``.

Supported actions are:

  - check if pull request source is mergeable
  - run aribitrary shell command on the on-disk representation of a source
    - flake8-diff is the only currently configured shell command

The only supported output is github issue comment.  A templating system
is made available for all outputs, so that the user can specify the text
made in the comment.

## Configuration example
The following configuration (expressed here as JSON) will listen for a webhook 
push for a new pull request for the repo "DT2/dt", and will run flake8diff 
on the checked-out pull request:

    {
        "name": "flake8_pull_request",
        "source": {
            "source_class": "pull_request",
            "criteria": {
                "repo": "DT2/dt"
            }
        },
        "actions": [
            {
                "name": "flake8diff",
                "task": "flake8_diff",
                "failure_handler": {
                    "name": "notify_error",
                    "task": "pull_request_comment",
                    "kwargs": {
                        "template": "Flake8 violations:\n\n{{ parent.output|indent(4, True) }}"
                    }
                }
            }
        ]
    }
    
Note here that `parent` refers to the return value of the `flake8_diff` task,
which is an instance of the class `CommandResult` which has an `output` attribute
that contains the stderr of the failed command.

In reality, this blob is stored in two model classes (Configuration and ConfigurationSource).

## Success/failure handlers
Each configured action can define success and failure handler.  These are actions
themselves, that are conditionally executed based on the result of the parent action.
The return value of the parent action is inspected, and if it is truthy, the success
handler is executed (otherwise, the failure handler).  Handlers are optional.
Note that this is distinct from celery's notion of task success and failure;
*task* failure should only occur if there is an exception that prevents the
execution of the task.  In pipeline, we want to distinguish between the 
failure of the task itself and the failure of the command executed by the
task (in fact, handlers are only executed if the task had a SUCCESS status).

An example of a failure handler might be a pull request comment that is
made only when the flake8-diff command returned a failure exit code 
(indicating that there were flake8 violations).

## Local setup
Note: you must set up ssh keys for communication with github.
Additinally, you must provide a github application token in the
environment variable PIPELINE_GITHUB_TOKEN.

Will use sqlite database.

### Install


    VIRTUALENV_PYTHON=`which python3` mkvirtualenv hamster-ci
    workon hamster-ci
    pip3 install -r requirements/base.txt -i https://pypi.python.org/simple
    DJANGO_SETTINGS_MODULE=hamster.settings python hamster/manage.py migrate
    DJANGO_SETTINGS_MODULE=hamster.settings python hamster/manage.py createsuperuser
    
#### OSX
Had some issues. May need to run before installing requirements:

    pip3 install --upgrade pip
    brew install pkg-config libffi
    export PKG_CONFIG_PATH=/usr/local/Cellar/libffi/3.0.13/lib/pkgconfig/
    
    ref: https://github.com/pypa/pip/issues/2104
    ref: http://stackoverflow.com/questions/22875270/error-installing-bcrypt-with-pip-on-os-x-cant-find-ffi-h-libffi-is-installed

    
#### Local dev install

    VIRTUALENV_PYTHON=`which python3` mkvirtualenv hamster-ci
    workon hamster-ci
    pip3 install -r requirements/base.txt  -r requirements/tests.txt -i https://pypi.python.org/simple
    DJANGO_SETTINGS_MODULE=hamster.local_settings python hamster/manage.py migrate
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

#### Authentication
One superuser is created for django admin: 

    hamster:hamster
    
## Deployment
Hamster CI is deployed using docker and fig (aka docker-compose).

The application architecture includes:

  - celery worker/s
  - gunicorn app workers
  - nginx for static files and for proxying to gunicorn
  - redis as the broker (TODO: rabbitmq)
  - postgresql database
  
### Host requirements

    - lxc-docker (*not* docker.io pkg)
    - fig
    
In order to make the docker daemon work behind a proxy, you need to add some 
configuration to your system, which varies depending on the host os.

Docker deployments also require ssh keypair in github.key/github.pub files with the 
public key registered in github, as well as user and email configured in the
gitconfig file.

### Local deployment
#### First deployment
The first deployment will initialize the database.  Subsequent deployments should not.

    make scratch
    
#### Subsequent deployments
If any requirements have changed, or any change requiring a docker rebuild:

    make update
    
If only python code has changed, you can get away with:

    make restart

#### Adding workers
Both app and celery worker have a default concurrency of 2, which is overridden
in the docker deployment to 6 (each).

In order to add more worker containers:

    fig scale worker=N
    fig scale app=N

(I have not tried this yet)

### Remote deployment
You must use a different virtualenv for remote deployment, since Fabric does 
not yet support python3.

	mkvirtualenv deployenv
	workon deployenv
    pip install -r requirements/deploy.txt
        
#### First deployment

    fab install:/home/username/hamster,git@github.dev.dealertrack.com:mike/hamster -H 1.2.3.4 -u username
    
#### Subsequent deployments

    fab deploy:/home/username/hamster
    
#### Jenkins CI

	virtualenv .
	. bin/activate
	pip install -r requirements/deploy.txt
	fab deploy:/home/username/hamster -H 1.2.3.4 -u username

## Adding code to pipeline

### Modules
Modules you want to use must be imported in pipeline.__init__.
This initializes registration of the classes contained in the module.

# The future
Build on pipeline to create a github comment bot, and use that bot to implement a review system for pull requests.

The system can leverage an external library that does static analysis??


# Issues
- need to disable strict host key chexking for github in order t run the tests, 
or to checkout anything.
http://serverfault.com/questions/447028/non-interactive-git-clone-ssh-fingerprint-prompt
$ echo -e "Host github.com\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config


# Tips




   Debugging an installed app or library inside hamster
   1. grab the source a sa submodule in your hamster working directory (on th ehost)
    - git submodule init
    - git submodule add <git url>
   2. Add the following line to worker.sh and app.sh, right before the last line:
     pip install -e /hamster/<library name>

    Use the 'make develop' command every time you reloa,d it will mount the source
    in as a volume, with your changes.  You do need to reload for every change, though.