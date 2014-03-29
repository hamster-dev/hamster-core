Development Notes
=================

Below are some notes on how to get your development environment setup and how
to get ready to contribute code.

Setting up your development environment
---------------------------------------

Clone the repo::

   $ git clone https://github.com/hamster-dev/hamster-core

Install requirements:

* VirtualBox - https://www.virtualbox.org
* Vagrant - http://www.vagrantup.com

Startup and provision the development VM::

   $ cd hamster-core
   $ vagrant up

You can now login to the VM::

   $ vagrant ssh

... and start up the site::

   $ cd hamster
   $ workon hamster
   $ python manage.py runserver 0.0.0.0:9000

You should see it running at http://localhost:9000
