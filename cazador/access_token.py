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


ACCESS_TOKEN_URL = os.environ.get(
    'CAZADOR_ACCESS_TOKEN_URL', 'https://trello.com/1/OAuthGetAccessToken'
)

@click.command()
@click.argument('key')
@click.argument('secret')
@click.argument('token')
@click.argument('token_secret')
@click.argument('verification')
def access_token(key, secret, token, token_secret, verification):
    """"Returns access token for cazador.

    Required arguments are API key and secret, request token and secret
    and verification code.
    """
    session = oauthlib.OAuth1Session(
        client_key=key, client_secret=secret,
        resource_owner_key=token, resource_owner_secret=token_secret,
        verifier=verification
    )
    access_token = session.fetch_access_token(ACCESS_TOKEN_URL)
    token = access_token['oauth_token']
    token_secret = access_token['oauth_token_secret']
    click.echo(
        'Token: {token}\nToken secret: {token_secret}'.format(**locals())
    )
    return token, token_secret


if __name__ == '__main__':
    access_token()
