#!/usr/bin/env python

"""
Mock HTTP server for generating github api webhook fixtures.
Accepts calls destined for github-api view and dumps to `dumpfile`/data.json.
Requires bottle library.
"""

import sys
import json
from bottle import route, run, request

@route('/github-api/hook/', method='POST')
def hookdump():
    if request.content_type == 'application/x-www-form-urlencoded':
        postdata = request.forms['payload']
        with open(dumpfile, 'w') as fh:
            fh.write(json.dumps({'payload': postdata}, indent=2))
    else:
        postdata = json.loads(request.body.read())
        with open(dumpfile, 'w') as fh:
            fh.write(json.dumps(postdata, indent=2))

    return "OK"

if len(sys.argv) > 1:
    dumpfile = sys.argv[1]
else:
    dumpfile = 'data.json'

run(host='0.0.0.0', port=9000, debug=True)