from __future__ import annotations

from typing import Any
from typing import TypeVar

from py_zipkin.storage import Stack
from py_zipkin.zipkin import create_http_headers_for_new_span
from typing_extensions import ParamSpec

from swagger_zipkin.decorate_client import Client
from swagger_zipkin.decorate_client import decorate_client
from swagger_zipkin.decorate_client import Resource

T = TypeVar('T', covariant=True)
P = ParamSpec('P')


class ZipkinResourceDecorator:
    """A wrapper to the swagger resource.

    :param resource: A resource object. eg. `client.pet`, `client.store`.
    :type resource: :class:`swaggerpy.client.Resource` or :class:`bravado_core.resource.Resource`
    """

    def __init__(self, resource: Client, context_stack: Stack | None = None) -> None:
        self.resource = resource
        self._context_stack = context_stack

    def __getattr__(self, name: str) -> Resource:
        return decorate_client(self.resource, self.with_headers, name)

    def with_headers(self, call_name: str, *args: Any, **kwargs: Any) -> Any:
        kwargs.setdefault('_request_options', {})
        request_options: dict = kwargs['_request_options']
        headers = request_options.setdefault('headers', {})

        headers.update(create_http_headers_for_new_span(
            context_stack=self._context_stack))
        return getattr(self.resource, call_name)(*args, **kwargs)

    def __dir__(self) -> list[str]:
        return dir(self.resource)


class ZipkinClientDecorator:
    """A wrapper to swagger client (swagger-py or bravado) to pass on zipkin
    headers to the service call.

    Even though client is initialised once, all the calls made will have
    independent spans.

    :param client: Swagger Client
    :type client: :class:`swaggerpy.client.SwaggerClient` or :class:`bravado.client.SwaggerClient`.
    """

    def __init__(self, client: Client, context_stack: Stack | None = None):
        self._client = client
        self._context_stack = context_stack

    def __getattr__(self, name: str) -> Client:
        return ZipkinResourceDecorator(
            getattr(self._client, name),
            context_stack=self._context_stack,
        )

    def __dir__(self) -> list[str]:
        return dir(self._client)  # pragma: no cover
