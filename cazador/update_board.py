#!/usr/bin/env python
#
# Copyright (c) 2015 Red Hat Inc.
#
# Author: Martin Magr mmag@redhat.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Use this script to setup token for cazador

import click
import importlib
import json
import requests
import requests_oauthlib as oauthlib
import os
import re
import sys

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


CONFIG_PATH = os.environ.get(
    'CAZADOR_CONFIG', os.path.expanduser('~/.cazador.conf')
)
# dynamically load required connectors
PREFIXES = os.environ.get('CAZADOR_CONNECTORS', 'bz,lp')
CONNECTORS = []
for prefix in PREFIXES.split(','):
    prefix = prefix.strip()
    CONNECTORS.append(
        (
            prefix,
            importlib.import_module(
                'cazador.connectors.{}connector'.format(prefix)
            )
        )
    )

TRELLO_URL_BASE = 'https://api.trello.com/1'
TRELLO_URL_LISTS = (
    '/boards/{board}/lists/?fields=name&cards=open&card_fields=name'
)
TRELLO_URL_CARD = '/cards'
TRELLO_CARD_ID_FMT = '[{id}]'
TRELLO_CARD_NAME_FMT = '[{id}] {summary}'
TRELLO_CARD_DESC_FMT = '''
[{id}] {summary}

component: {component}
priority: {priority}
status: {status}
url: {url}
'''


@click.command()
@click.option(
    '-n', '--new-list',
    default='New',
    help='Name of list where new cards with bugs should be created.'
)
@click.option(
    '-f', '--finished-list',
    default='(Complete|Sprint.*)',
    help='Name or regex of list(s) where finished cards are stored.'
)
@click.argument('board')
def update_board(board, new_list=None, finished_list=None):
    # load config file
    config = configparser.SafeConfigParser()
    if not config.read(CONFIG_PATH):
        click.echo('Failed to parse config file {}.'.format(CONFIG_PATH))
        sys.exit(1)
    if not config.has_section('trello'):
        click.echo('Config file does not contain section [trello].')
        sys.exit(1)
    trello_creds = dict(config.items('trello'))
    trello_vars = ('api_key', 'api_secret', 'access_token', 'access_secret')
    if len(set(trello_creds.keys()) and set(trello_vars)) != 4:
        click.echo(
            'Config file does not contain one or more from following variables'
            ' in section [trello]: {}'.format(trello_vars)
        )
        sys.exit(1)
    # authenticate to Trello
    trello_auth = oauthlib.OAuth1(
        client_key=trello_creds['api_key'],
        client_secret=trello_creds['api_secret'],
        resource_owner_key=trello_creds['access_token'],
        resource_owner_secret=trello_creds['access_secret']
    )
    # load current unfinished cards
    current = []
    _locals = locals()
    req = requests.get(
        '{}{}'.format(TRELLO_URL_BASE, TRELLO_URL_LISTS.format(**_locals)),
        auth=trello_auth
    )
    if req.status_code != 200:
        click.echo('Failed to load Trello cards: {}'.format(req.reason))
        sys.exit(1)
    new_list_id = None
    for board_list in req.json():
        if re.match(finished_list, board_list['name']):
            continue
        if not new_list_id and board_list['name'] == new_list:
            new_list_id = board_list['id']
        current.extend(board_list['cards'])
    if not new_list_id:
        click.echo('Could not find list {}'.format(new_list))
        sys.exit(1)
    # run through all connectors and create new cards from bugs
    for prefix, module in CONNECTORS:
        try:
            module_creds = dict(config.items('{}:connector'.format(prefix)))
        except configparser.NoSectionError:
            continue
        connector = module.Connector(
            user=module_creds.get('user', None),
            password=module_creds.get('password', None)
        )
        for bug in connector.query(**json.loads(module_creds['query'])):
            cid = TRELLO_CARD_ID_FMT.format(id=bug.id)
            name = TRELLO_CARD_NAME_FMT.format(id=bug.id, summary=bug.summary)
            for i in current:
                if i['name'].startswith(cid):
                    click.echo('Skipping card for {}.'.format(cid))
                    break
            else:
                click.echo('Creating card for {}.'.format(cid))
                req = requests.post(
                    '{}{}'.format(TRELLO_URL_BASE, TRELLO_URL_CARD),
                    auth=trello_auth,
                    data={
                        'idList': new_list_id,
                        'name': name,
                        'desc': TRELLO_CARD_DESC_FMT.format(
                            id=bug.id,
                            summary=bug.summary,
                            component=bug.component,
                            priority=bug.priority,
                            status=bug.status,
                            url=bug.url
                        )
                    }
                )


if __name__ == '__main__':
    update_board()
