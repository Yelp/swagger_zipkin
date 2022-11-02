#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup


setup(
    name='swagger_zipkin',
    version="0.5.1",
    provides=["swagger_zipkin"],
    author='Yelp, Inc.',
    author_email='opensource+swagger-zipkin@yelp.com',
    license='Copyright Yelp 2016',
    url="https://github.com/Yelp/swagger_zipkin",
    description='Zipkin decorators for swagger clients - swagger-py and bravado.',
    packages=find_packages(exclude=['tests*']),
    python_requires=">=3.7",
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
