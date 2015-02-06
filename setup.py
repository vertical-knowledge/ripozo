__author__ = 'Tim Martin'
from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'VERSION')) as f:
    version = f.read().strip()

setup(
    name='ripozo',
    version=version,
    packages=['rest', 'rest.managers', 'rest.viewsets'],
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
    ]
)
