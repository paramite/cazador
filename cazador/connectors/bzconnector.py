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
# Red Hat Bugzilla connector

import bugzilla
import os

from .base import ConnectorBug


BUGZILLA_URL = os.environ.get(
    'CAZADOR_BUGZILLA_URL', 'https://bugzilla.redhat.com/xmlrpc.cgi'
)
BUGZILLA_BUGS_URL = os.environ.get(
    'CAZADOR_BUGZILLA_BUGS_URL',
    'https://bugzilla.redhat.com/show_bug.cgi?id={}'
)

class Connector:
    def __init__(self, user=None, password=None):
        self._conn = bugzilla.RHBugzilla(
            url=BUGZILLA_URL, user=user, password=password
        )

    def __getattr__(self, attr):
        return getattr(self._conn, attr)

    # {'product': ['product', 'product'],
    #  'component': ['component','component'],
    #  'status': 'status'}
    def query(self, **kwargs):
        """Bugzilla query result generator."""
        for bug in self._conn.query(kwargs):
            yield ConnectorBug(
                id='bz#{}'.format(bug.bug_id),
                summary='{}{}'.format(
                    bug.summary[:50], '...' if len(bug.summary) > 50 else ''
                ),
                component=bug.component,
                status=bug.status,
                priority=bug.priority,
                url=BUGZILLA_BUGS_URL.format(bug.bug_id),
            )
