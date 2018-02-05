#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import find_packages
from setuptools import setup

from swagger_zipkin import __version__


setup(
    name='swagger_zipkin',
    version=__version__,
    provides=["swagger_zipkin"],
    author='Yelp, Inc.',
    author_email='opensource+swagger-zipkin@yelp.com',
    license='Copyright Yelp 2016',
    url="https://github.com/Yelp/swagger_zipkin",
    description='Zipkin decorators for swagger clients - swagger-py and bravado.',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'py_zipkin>=0.10.1',
    ],
    keywords='zipkin',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
