# Hamster CI
![Hamster](http://i5.glitter-graphics.org/pub/1933/1933385pgqm471nc2.jpg)

A distributed python3 system that reacts to github events, allowing a user to specify a
pipeline of tasks to be executed when these events occur.  The pipeline are executed on 
remote workers, using the `celery` library.

Hamster knows how to 
  - interact with github
  - execute developer-defined, runtime-configured python functions 


Tasks are configured in code, which is read by the appserver when a 
triggering event occurs, and then scheduled to be executed on a worker.


Tasks, while technically distributed across nodes, are executed
serially in a data sharing pipeline, using the `pipeline` library.


# Technical overview

    Event --> EventSubscriber --> Pipeline

Input entering the system is serialized to an `Event`.
Events expose the serialized input data as a property, which 
is carried forward through the rest of the system.  Currently the
input entering the system are Github webhooks, and the resultant Events
expose connected github3 objects (like `github3.pulls.PUllRequest` et al).

When an event occurs, the system is searched for matching `EventSubscribers`.
Subscribers contain the tasks which are to be scheduled and the parameters with which those tasks are executed.  


# Using Hamster
Hamster is packaged with all the code necessary for deployment inside Docker
containers.  
The application architecture includes:

  - celery worker/s
  - gunicorn app workers
  - nginx for static files and for proxying to gunicorn
  - redis as the broker
  - postgresql database

In order to get a running hamster, there are a few prerequisites.

## Prerequisites
### 1. Runtime environment variables
Hamster requires some information, stored in environment variables.

Required variables are:

  - HAMSTER_GITHUB_API_TOKEN - a valid github API token
  - HAMSTER_GITHUB_API_USER - username for above token
These variables are used for connectig to github via it's REST API.

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
If you wish to test hamster out without docker, you can.
You will need redis running, and two terminals (app/worker).
This will use sqlite as the database.
Github ssh authentication will default to your user account's ssh keys.

### Install

    pip install -r requirements.txt
    export DJANGO_SETTINGS_MODULE=hamster.local_settings 
    python hamster/manage.py migrate
    # below is an interactive command. if you wish to script it, see example in app.sh
    python hamster/manage.py createsuperuser
    
### Run
#### Web app

    export HAMSTER_GITHUB_API_TOKEN=abcdefg123456
    export HAMSTER_GITHUB_API_USER=username
    export HAMSTER_GITHUB_HOST=github-enterprise.whatever  # optional
    export DJANGO_SETTINGS_MODULE=hamster.local_settings 
    python hamster/manage.py runserver --nothreading  # local settings use sqlite

#### Worker

    export HAMSTER_GITHUB_API_TOKEN=abcdefg123456
    export HAMSTER_GITHUB_API_USER=username
    export HAMSTER_GITHUB_HOST=github-enterprise.whatever  # optional
    export DJANGO_SETTINGS_MODULE=hamster.local_settings 
    cd hamster
    celery -A hamster worker -l debug
    
