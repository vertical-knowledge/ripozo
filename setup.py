__author__ = u'Tim Martin'
__pkg_name__ = u'ripozo'
from setuptools import setup, find_packages

version = '0.1.8'

setup(
    name=__pkg_name__,
    version=version,
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    description='An tool for easily making RESTful interfaces',
    author=__author__,
    author_email='tim.martin@vertical-knowledge.com',
    install_requires=['six>=1.4.1,!=1.7.1', 'jinja2'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    tests_require=[
        'tox',
        'mock',
        'ripozo-tests'
    ],
    test_suite="tests"
)
