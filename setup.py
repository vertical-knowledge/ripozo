from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from setuptools import setup, find_packages

__author__ = 'Tim Martin'
__pkg_name__ = 'ripozo'

version = '1.3.1.dev0'

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
    description='ReSTful API framework with HATEOAS support and compatibility with Flask, Django, SQLAlchemy and more.',
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
    install_requires=[
        'six>=1.4.1,!=1.7.1',
        'werkzeug'
    ],
    keywords='REST HATEOAS Hypermedia RESTful SIREN HAL API JSONAPI web framework Django Flask SQLAlchemy Cassandra',
    name='ripozo',
    packages=find_packages(include=['ripozo', 'ripozo.*']),
    tests_require=[
        'unittest2',
        'tox',
        'mock'
    ],
    test_suite="ripozo_tests",
    url='http://ripozo.readthedocs.org/',
    version=version
)
