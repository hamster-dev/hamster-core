Hamster Continous Integration
=============================

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
