__author__ = 'Tim Martin'
from setuptools import setup
import os

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

version = (0, 2, 1, 'b28')
__version__ = '.'.join(map(str, version))

setup(
    name='flask-cassandra-rest',
    version=__version__,
    packages=['rest', 'rest.managers', 'rest.viewsets'],
    include_package_data=True,
    description='An tool for easily making cassandra RESTful interfaces',
    author='Tim Martin',
    author_email='tim.martin@vertical-knowledge.com',
    install_requires=['Flask', 'cqlengine', 'webargs', 'Flask-SQLAlchemy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
