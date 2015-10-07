#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='cazador',
    version='0.1',
    author='Martin Magr',
    author_email='mmagr@redhat.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'requests_oauthlib',
        'python-bugzilla',
        'launchpadlib'
    ],
    entry_points={
        'console_scripts': [
            'cazador_request_token = cazador.request_token:request_token',
            'cazador_access_token = cazador.access_token:access_token',
            'cazador_update_board = cazador.update_board:update_board'
        ],
    }
)
