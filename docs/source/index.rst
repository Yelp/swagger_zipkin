swagger_zipkin |version|
============================

:mod:`swagger_zipkin` contains zipkin integration tools for instrumenting downstream
 service calls made using `bravado <http://bravado.readthedocs.org/en/latest/>`_ or
`swagger-py <http://swagger-py.readthedocs.org/en/latest/>`_ http clients.

It is aimed to be a standalone package, with only dependancy being
`pyramid_zipkin <https://github.com/Yelp/pyramid_zipkin>`_.

The limitations are that the service should run on
`Pyramid framework<http://docs.pylonsproject.org/en/latest/docs/pyramid.html>`_
and use `pyramid_zipkin <https://github.com/Yelp/pyramid_zipkin>`_ for zipkin
integration.

Quick Start
-----------

    The decorator can be applied to any swagger-py or bravado client. The example
    shows a sample usage on bravado. It assume the code is being called from within
    a pyramid view.

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
