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
import requests
import requests_oauthlib as oauthlib
import os


REQUEST_TOKEN_URL = os.environ.get(
    'CAZADOR_REQUEST_TOKEN_URL', 'https://trello.com/1/OAuthGetRequestToken'
)
TOKEN_AUTH_URL = os.environ.get(
    'CAZADOR_TOKEN_AUTH_URL', 'https://trello.com/1/OAuthAuthorizeToken'
)

@click.command()
@click.option(
    '-e', '--expire',
    default='never',
    help='Time for which token should be valid (for example "14days").'
)
@click.argument('key')
@click.argument('secret')
def request_token(key, secret, expire=None):
    """Returns request token for cazador.

    Required arguments are API key and API secret.

    Request token has to be authorized on printed URL and then accessed
    by cazador_access_token.
    """
    session = oauthlib.OAuth1Session(client_key=key, client_secret=secret)
    response = session.fetch_request_token(REQUEST_TOKEN_URL)
    token = response.get('oauth_token')
    token_secret = response.get('oauth_token_secret')

    _locals = locals()
    _locals['TOKEN_AUTH_URL'] = TOKEN_AUTH_URL
    click.echo(
        'Token: {token}\nToken secret: {token_secret}'.format(**_locals)
    )
    click.echo(
        'Authorize on: {TOKEN_AUTH_URL}?name=cazador&scope=read,write'
        '&oauth_token={token}&expiration={expire}'.format(**_locals)
    )
    return token, token_secret


if __name__ == '__main__':
    request_token()
