swagger_zipkin |version|
============================

:mod:`swagger_zipkin` contains zipkin integration tools for instrumenting downstream service calls made using `bravado <http://bravado.readthedocs.org/en/latest/>`_ or `swagger-py <http://swagger-py.readthedocs.org/en/latest/>`_ http clients.

It is aimed to be a standalone package, with only dependency being `py_zipkin <https://github.com/Yelp/py_zipkin>`_.

Quick Start
-----------

The decorator can be applied to any swagger-py or bravado client. The example
shows a sample usage on bravado. It assume the code is being called from within
a `py_zipkin.zipkin.zipkin_span` context manager or decorator.

.. code-block:: python

    from bravado.client import SwaggerClient
    from swagger_zipkin.zipkin_decorator import ZipkinClientDecorator

    client = SwaggerClient.from_url("http://petstore.swagger.io/v2/swagger.json")
    zipkin_wrapped_client = ZipkinClientDecorator(client)

    pet = zipkin_wrapped_client.pet.getPetById(petId=42).result()

Contents
--------

.. toctree::
   :maxdepth: 1

   swagger_zipkin
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
