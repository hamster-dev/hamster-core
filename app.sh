#!/bin/bash

# Boot the app.
# Run migrations, setup superuser, and run gunicorn.

NUM_WORKERS=${NUM_WORKERS:-2}
USER=hamster
PASSWD=hamster

source util.sh

# block until postgres is available (or else django migrate will fail)
check_up "postgres" ${DB_PORT_5432_TCP_ADDR} 5432

develop_pkgs

cd hamster

su -m hamster -c "python manage.py migrate"

# check if user table is empty, if it is create the superuser.  TODO make this not suck
usertable=$(echo "select * from auth_user;" | python manage.py dbshell)
echo ${usertable} |grep "0 rows" >/dev/null
if [[ $? -eq 0 ]]; then
	echo "from django.contrib.auth.models import User; User.objects.create_superuser('${USER}', '', '${PASSWD}')" | su -m hamster -c "python manage.py shell"
fi

# don't su this command, as we want it's owner to be root, these will be served by nginx
#TODO: dont run this as root, as it leaves behind some root-owned file that
# the docker user cannot delete
python manage.py collectstatic --noinput

su -m hamster -c "gunicorn --bind 0.0.0.0:8000 --workers ${NUM_WORKERS} hamster.wsgi:application"
