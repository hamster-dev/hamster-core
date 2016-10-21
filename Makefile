# Workflows:
#
#   1. (Re)build the system from scratch.
#	Stops running containers and deletes all images:
#		make scratch
#
#	2. The code has been updated; build updated images,
#	stop running app and worker containers, purge ap and worker images,
#	and restart.
#		make update

.DEFAULT_GOAL := build

scratch: check install run
update: build refresh run
update-and-watch: build refresh run-nodaemon


# check for deps
check:
	ls gitconfig
	ls github.pub
	ls github.key

# build docker images
build:
	docker-compose build

# install from scratch
install: clean build

run:
	docker-compose up -d

run-nodaemon:
	docker-compose up

develop:
	docker-compose -f docker-compose-dev.yml up

# restart the containers, if there were local source changes
restart: stop-app run

# remove app and worker containers so they can be updated;
clean-app:
	docker-compose rm --force app worker

stop-app:
	-docker-compose stop app worker

# only need to refresh app and worker, as the rest are just dloaded from docker hub
refresh: stop-app clean-app

kill: stop
	-docker-compose kill

stop:
	-docker-compose stop

# stop all running containers, and then remove their images
clean: kill
	docker-compose rm --force
