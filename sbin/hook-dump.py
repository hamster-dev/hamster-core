#!/usr/bin/env python

"""
Mock HTTP server for generating github api webhook fixtures.
Accepts calls destined for github-api view and dumps to `dumpfile`/data.json.
Requires bottle library.

Note: you can avoid having to use this completely by going to your
repository's webhook settings and copying the JSON from one of the
hooks in the webhook logs.
"""

import sys
import json
from bottle import route, run, request


PORT=9000
@route('/github-api/hook/', method='POST')
def hookdump():
    if event_filter and not request.headers.get('X-GITHUB-EVENT') == event_filter:
        return "OK"

    if request.content_type == 'application/x-www-form-urlencoded':
        postdata = request.forms['payload']
        with open(dumpfile, 'w') as fh:
            fh.write(json.dumps({'payload': postdata}, indent=2))
    else:
        postdata = json.loads(request.body.read())
        with open(dumpfile, 'w') as fh:
            fh.write(json.dumps(postdata, indent=2))

    return "OK"

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='dumpfile', default='data.json')
parser.add_argument('--filter', dest='event_filter', default=None)

args = parser.parse_args()
dumpfile = args.dumpfile
event_filter = args.event_filter

run(host='0.0.0.0', port=PORT, debug=True)