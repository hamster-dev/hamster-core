Development Notes
=================

Below are some notes on how to get your development environment setup and how
to get ready to contribute code.

Setting up your development environment
---------------------------------------

Install requirements:

* VirtualBox - https://www.virtualbox.org
* Vagrant - http://www.vagrantup.com

Clone the repo::

   $ git clone https://github.com/hamster-dev/hamster-core

Startup and provision the development VM::

   $ cd hamster-core
   $ vagrant up

Assuming that went well, you can now login to the VM::

   $ vagrant ssh

Initial setup of the virtualenv and site::

   $ mkvirtualenv hamster
   $ cd /vagrant
   $ pip install -Ur hamster/requirements.pip
   $ python manage.py syncdb --migrate

... and start up the site::

   $ python manage.py runserver 0.0.0.0:8000

You should see it running at http://localhost:9000
