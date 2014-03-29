Hamster Continous Integration
=============================

[![Build Status](https://api.travis-ci.org/hamster-dev/hamster-core.svg)](https://travis-ci.org/hamster-dev/hamster-core) [![Coverage Status](https://coveralls.io/repos/hamster-dev/hamster-core/badge.png?branch=master)](https://coveralls.io/r/hamster-dev/hamster-core?branch=master)

Jenkins needs to go, and Travis CI is great for public projects, but sucks at
internal CI for commercial stuff, so we figured the world could use another
CI project.

This one is built with Django and uses some fairly basic stuff:

* django-rest-framework - Internal API
* celery - workers and build jobs
* AngularJS - UI

The features are minimal, but here's what this will do, someday:

* Distributed builds - just add more celery workers on the OS you want
* Simple configuration stored with your code (minimal config in the UI)
* Complete RESTful API
* Integration with Github (and Github Enterprise) and possibly other code
  hosting places like Bitbucket
* Really simple local installation

### Links

* Docs - http://hamster.readthedocs.org
