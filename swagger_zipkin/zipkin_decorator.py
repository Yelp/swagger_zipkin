# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from py_zipkin.zipkin import create_http_headers_for_new_span

from swagger_zipkin.decorate_client import decorate_client


class ZipkinResourceDecorator(object):
    """A wrapper to the swagger resource.

    :param resource: A resource object. eg. `client.pet`, `client.store`.
    :type resource: :class:`swaggerpy.client.Resource` or :class:`bravado_core.resource.Resource`
    """

    def __init__(self, resource):
        self.resource = resource

    def __getattr__(self, name):
        return decorate_client(self.resource, self.with_headers, name)

    def with_headers(self, call_name, *args, **kwargs):
        kwargs.setdefault('_request_options', {})
        headers = kwargs['_request_options'].setdefault('headers', {})

        headers.update(create_http_headers_for_new_span())
        return getattr(self.resource, call_name)(*args, **kwargs)


class ZipkinClientDecorator(object):
    """A wrapper to swagger client (swagger-py or bravado) to pass on zipkin
    headers to the service call.

    Even though client is initialised once, all the calls made will have
    independent spans.

    :param client: Swagger Client
    :type client: :class:`swaggerpy.client.SwaggerClient` or :class:`bravado.client.SwaggerClient`.
    """

    def __init__(self, client):
        self.client = client

    def __getattr__(self, name):
        return ZipkinResourceDecorator(getattr(self.client, name))

    def __dir__(self):
        return dir(self.client)  # pragma: no cover
