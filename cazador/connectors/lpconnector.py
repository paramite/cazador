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
# Canonical Launchpad connector

import os

from launchpadlib.launchpad import Launchpad
from .base import ConnectorBug


class Connector:
    def __init__(self, user=None, password=None):
        # anonymous login is enough here
        self._conn = Launchpad.login_anonymously('cazador', 'production')

    def query(self, project=None, status=None):
        """Launchpad query result generator."""
        # only project and status is currently supported
        project = project or []
        status = status or []
        if not project:
            raise TypeError('Parameter "project" is required')
        for proj in project:
            for task in self._conn.projects[proj].searchTasks(status=status):
                yield ConnectorBug(
                    id='lp#{}'.format(task.bug.id),
                    summary='{}{}'.format(
                        task.bug.title[:50],
                        '...' if len(task.bug.title) > 50 else ''
                    ),
                    component=proj,
                    status=task.status,
                    priority=task.importance,
                    url=task.bug.web_link,
                )
