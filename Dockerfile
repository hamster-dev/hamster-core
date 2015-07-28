# Notes:
# The tactic here is to take advantage of the build context being added, to
# just install the dependencies in advance.
# So, the image generated does not contain the app, just the installed deps.
# Then, we mount the app as a volume into the container at runtime.
# This is a good tactic for development, because you don't have to build the
# image for every code change (unless there is a requirement change).
# This is a bad tactic for prod, because you can't tag your image with
# the code version and have that tag be reliable.
# When docker-compose 1.3 comes out, with capability like `docker-build -f Dockerfile`,
# we can use this technique in only the dev Dockerfile, and have a prod
# Dockerfile that actually (correctly) pulls the app from the build context
# and installs it.

FROM python:3.4

RUN apt-get update

# These are broken out b/c the network where I'm writing code is hella flaky,
# the docker image layer cache is a huge boon.
RUN apt-get -y install postgresql-client
RUN apt-get -y install sudo

# Why this line is required, again, I will *never* understand.
RUN apt-get update

# Even though the app runs on py3, we still need to support py2 tasks.
# This will be removed once we can direct tasks to celery workers
# based on the workspace type requested by the user.  For now, all
# workers will get a python2 install, since that is what we need hamster
# for.
RUN apt-get -y install python2.7
RUN apt-get -y install python-pip
RUN apt-get -y install python-virtualenv
RUN apt-get -y install python-dev

# Create a user for running app and worker
RUN adduser --home=/home/hamster --disabled-password --gecos '' hamster

#FIXME
# This is needed if you want workspaces to run processes as a different user
# than the app/worker user. can be removed if users are always the same.
# (user needs sudo to determine what the environment is for workspace user)
RUN usermod -a hamster -G sudo

# Add github ssh keys.
RUN mkdir -p /home/hamster/.ssh
ADD github.key /home/hamster/.ssh/id_rsa
ADD github.pub /home/hamster/.ssh/id_rsa.pub
RUN chmod 600 /home/hamster/.ssh/id_rsa
RUN chmod 644 /home/hamster/.ssh/id_rsa.pub
RUN chown -R hamster:hamster /home/hamster/.ssh

# Add git ident
ADD gitconfig /home/hamster/.gitconfig

# This is a hack, psycopg setup.py has some issues with a proxy and HOST header
RUN pip3 install cffi six

# This is another hack, without it pipeline doesnt install correctly
RUN pip3 install idna

ENV PYTHONUNBUFFERED 1
WORKDIR hamster

# This does not actually install the app, just it's dependencies.
# The app is mounted as a volume in docker-compose.
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD requirements-runtime.txt requirements-runtime.txt
RUN pip3 install -r requirements-runtime.txt

# Some crapola with py3 compat for pyopenssl pkg
# File "/usr/local/lib/python3.4/site-packages/ndg/httpsclient/ssl_peer_verification.py", line 17
#   except ImportError, e:
# SyntaxError: invalid syntax
RUN rm -rf /usr/local/lib/python3.4/site-packages/ndg*

RUN pip3 freeze