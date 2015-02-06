__author__ = 'Tim Martin'
from setuptools import setup, find_packages
from os import path

version = '0.1.0'

setup(
    name='ripozo',
    version=version,
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    description='An tool for easily making cassandra RESTful interfaces',
    author='Tim Martin',
    author_email='tim.martin@vertical-knowledge.com',
    install_requires=['six'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite="tests"
)
