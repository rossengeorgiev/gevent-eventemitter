#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(here, 'eventemitter/__init__.py'), encoding='utf-8') as f:
    __version__ = f.readline().split('"')[1]

setup(
    name='gevent-eventemitter',
    version=__version__,
    description='Implements EventEmitter using gevent',
    long_description=long_description,
    url='https://github.com/rossengeorgiev/gevent-eventemitter',
    author="Rossen Georgiev",
    author_email='rossen@rgp.io',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
    keywords='gevent event emitter ee greenlet',
    packages=['eventemitter'],
    install_requires=[
        'gevent>=1.3',
        ],
    zip_safe=True,
)
