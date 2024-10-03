#!/usr/bin/python3

# Copyright (c) 2024 Marek Beckmann
# Contributor - hashfunktion - Jesse Reppin

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
import json
import sys
import argparse

# STATES
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# Icinga Message
message = {
    'status': OK,
    'summary': 'Zammad Health Message: ',
}


def check(server, token):

    try:
        response = requests.get(
            f"{server}/api/v1/monitoring/health_check?token={token}")
        
        response.raise_for_status()

        zammad_data = response.json()
        status = UNKNOWN

    except requests.exceptions.RequestException as e:
        status = WARNING
        message['summary'] = f"Zammad Health information retrieval failed! Error: {str(e)}"
        return status
    except json.JSONDecodeError:
        status = WARNING
        message['summary'] = "Failed to parse JSON response from Zammad!"
        return status

    health = zammad_data['healthy']
    issues = zammad_data['issues']

    if health:
        status = OK
        message['summary'] += 'Zammad healthy'
        if not issues:
            message['summary'] += ' - no issues!'
        if issues:
            message['summary'] += '\nIssues: \n' + '\n'.join(issues)

    else:
        status = CRITICAL
        message['summary'] += 'Zammad not healthy - see Issues below!'
        if issues:
            message['summary'] += '\nIssues:\n' + '\n'.join(issues)

    return status


def args():
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='Icinga/Nagios Check Script for Zammad',
        epilog="Thanks for using my Plugin. \nDocumentation: https://github.com/marekbeckmann/Icinga2-Zammad-Check"
    )

    parser.add_argument(
        "--token",
        help="Specify the Zammad Monitoring Token.",
        required=True,
        action='store',
        type=str
    )

    parser.add_argument(
        "--server",
        required=True,
        action='store',
        type=str
    )

    return parser


args = args().parse_args()
token = args.token
server = args.server

message['status'] += check(server, token)
print("{summary}".format(
    summary=message.get('summary'),
))
raise SystemExit(message['status'])
