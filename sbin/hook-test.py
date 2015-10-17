#!/usr/bin/env python

# Emulate hithub hookshot
import os
import argparse
import sys
import requests
import json

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='fixture', default='pull_request.opened')
parser.add_argument('-s', dest='host', default='localhost')
parser.add_argument('-p', dest='port', default='8000')

args = parser.parse_args()

fixture_file = os.path.join(
    os.path.dirname(__file__), 
    os.pardir,
    'hamster', 'pullman', 'tests', 'fixtures', 'webhooks',
    '{}.json'.format(args.fixture)
)
try:
    with open(fixture_file, 'r') as fh:
        data = fh.read()
    
    response = requests.post(
        'http://{}:{}/pullman/hook/'.format(args.host, int(args.port)),
        json=json.loads(data),
        headers={
            'x-github-event': args.fixture.split('.')[0],
            #'content-type': 'application/json'
        }
    )

except IOError:
    print('no fixture file found')
    sys.exit(1)


