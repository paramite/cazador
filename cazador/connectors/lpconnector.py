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


LAUNCHPAD_BUGS_URL = os.environ.get(
    'CAZADOR_LAUNCHPAD_BUGS_URL',
    'https://bugs.launchpad.net/{}/+bug/{}'
)


class Connector:
    def __init__(self, user=None, password=None):
        pass

    def __getattr__(self, attr):
        pass

    def query(self, **kwargs):
        """Launchpad query result generator."""
        raise StopIteration()
