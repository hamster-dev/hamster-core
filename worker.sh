#!/bin/bash

# Boot the worker.
# Much of this cannot be done in the Dockerfile,
# since we only know the github host at runtime

DEBUG=${HAMSTER_DEBUG:1}
NUM_WORKERS=${NUM_WORKERS:-2}

source util.sh

# dont start worker until db is ready?
check_up "postgres" ${DB_PORT_5432_TCP_ADDR} 5432

echo "Github: ${HAMSTER_GITHUB_HOST}"

# dammit proxies
export no_proxy="localhost,${HAMSTER_GITHUB_HOST}"
export NO_PROXY=${no_proxy}

# debug github connectivity
[[ $DEBUG -eq 0 ]] && curl -I "https://${HAMSTER_GITHUB_HOST}/api"


#TODO: only do this if it's not already set
echo -e 'Host ${PIPELINE_GITHUB_HOST}\n\tStrictHostKeyChecking no\n' >> /home/hamster/.ssh/config
ssh-keyscan -t rsa ${HAMSTER_GITHUB_HOST} 2>&1 >> /home/hamster/.ssh/known_hosts

# debug github auth
if [[ ! -z $HAMSTER_GITHUB_HOST ]]; then
	[[ $DEBUG -eq 0 ]] && ssh -vT git@${HAMSTER_GITHUB_HOST}
fi

develop_pkgs

su -m hamster -c "cd hamster && celery worker -A hamster --concurrency=${NUM_WORKERS}"
