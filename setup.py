from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Tim Martin'
__pkg_name__ = 'ripozo'

from setuptools import setup, find_packages

import os

version = '1.2.0'

base_dir = os.path.dirname(__file__)

setup(
    author=__author__,
    author_email='tim.martin@vertical-knowledge.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description='A tool for easily making RESTful interfaces',
    extras_require={
        'examples': [
            'flask',
            'requests',
            'sqlalchemy',
        ],
        'docs': [
            'sphinx'
        ]
    },
    include_package_data=True,
    install_requires=[
        'six>=1.4.1,!=1.7.1'
    ],
    keywords='REST HATEOAS Hypermedia RESTful SIREN HAL API JSONAPI web framework',
    name='ripozo',
    packages=find_packages(exclude=['tests', 'tests.*']),
    tests_require=[
        'unittest2',
        'tox',
        'mock',
    ],
    test_suite="ripozo_tests",
    url='http://ripozo.readthedocs.org/',
    version=version
)
