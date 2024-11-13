from __future__ import annotations

import importlib
from contextlib import contextmanager
from typing import Any
from typing import TYPE_CHECKING
from typing import TypeVar

from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.span import format_span_id
from opentelemetry.trace.span import format_trace_id
from opentelemetry.trace.span import TraceFlags
from typing_extensions import ParamSpec

from swagger_zipkin.decorate_client import Client
from swagger_zipkin.decorate_client import decorate_client
from swagger_zipkin.decorate_client import Resource

if TYPE_CHECKING:
    # pragma: no cover
    import pyramid.request.Request  # type: ignore[import-untyped]

T = TypeVar('T', covariant=True)
P = ParamSpec('P')

tracer = trace.get_tracer("otel_decorator")


class OtelResourceDecorator:
    """A wrapper to the swagger resource.

    :param resource: A resource object. eg. `client.pet`, `client.store`.
    :type resource: :class:`swaggerpy.client.Resource` or :class:`bravado_core.resource.Resource`
    """

    def __init__(self, resource: Client, client_identifier: str, smartstack_namespace: str) -> None:
        self.resource = resource
        self.client_identifier = client_identifier
        self.smartstack_namespace = smartstack_namespace

    def __getattr__(self, name: str) -> Resource:
        return decorate_client(self.resource, self.with_headers, name)

    def with_headers(self, call_name: str, *args: Any, **kwargs: Any) -> Any:
        kwargs.setdefault('_request_options', {})
        request_options: dict = kwargs['_request_options']
        request_options.setdefault('headers', {})

        request = get_pyramid_current_request()
        http_route = getattr(request, "matched_route", "")
        http_request_method = getattr(request, "method", "")

        parent_span = trace.get_current_span()
        span_name = f"{http_request_method} {http_route}"
        with tracer.start_as_current_span(
            span_name, kind=trace.SpanKind.CLIENT
        ) as span:
            self.inject_otel_headers(kwargs, span)
            self.inject_zipkin_headers(kwargs, span, parent_span)

            # ideally the exception should be scoped for self.with_headers 
            # handle_exception should handle general excetion and the specific exception HTTPError 
            # But this would create a dependency on bravado package. Is this ok?
            # Assuming resource.operation does throw HTTPError
            # https://github.com/Yelp/bravado/blob/master/bravado/exception.py
            with self.handle_exception():
                span.set_attribute("url.path", getattr(request, "path", ""))
                span.set_attribute("http.route", http_route)
                span.set_attribute("http.request.method", http_request_method)

                span.set_attribute("client.namespace", self.client_identifier)
                span.set_attribute("peer.service", self.smartstack_namespace)
                span.set_attribute("server.namespace", self.smartstack_namespace)
                span.set_attribute("http.response.status_code", "200")

                return getattr(self.resource, call_name)(*args, **kwargs)

    @contextmanager
    def handle_exception(
        self,
    ) -> Any:
        try:
            yield
        except Exception as e:
            span = trace.get_current_span()
            span.set_attribute("error.type", e.__class__.__name__)
            span.set_attribute("http.response.status_code", "500")
            raise e

    def __dir__(self) -> list[str]:
        return dir(self.resource)  # pragma: no cover

    def inject_otel_headers(
        self, kwargs: dict[str, Any], current_span: trace.Span
    ) -> None:
        propagator = TraceContextTextMapPropagator()
        carrier = kwargs['_request_options']["headers"]
        propagator.inject(carrier=carrier, context=trace.set_span_in_context(current_span))


    def inject_zipkin_headers(
            self, kwargs: dict[str, Any], current_span: trace.Span, parent_span: trace.Span
    ) -> None:
        current_span_context = current_span.get_span_context()
        kwargs["_request_options"]["headers"]["X-B3-TraceId"] = format_trace_id(
            current_span_context.trace_id
        )
        kwargs["_request_options"]["headers"]["X-B3-SpanId"] = format_span_id(
            current_span_context.span_id
        )
        if parent_span is not None and parent_span.is_recording():
            parent_span_context = parent_span.get_span_context()
            kwargs["_request_options"]["headers"]["X-B3-ParentSpanId"] = format_span_id(
            parent_span_context.span_id)

        kwargs["_request_options"]["headers"]["X-B3-Sampled"] = (
            "1"
            if (current_span_context.trace_flags & TraceFlags.SAMPLED == TraceFlags.SAMPLED)
            else "0"
        )
        kwargs["_request_options"]["headers"]["X-B3-Flags"] = "0"


class OtelClientDecorator:
    """A wrapper to swagger client (swagger-py or bravado) to pass on zipkin
    headers to the service call.

    Even though client is initialised once, all the calls made will have
    independent spans.

    :param client: Swagger Client
    :type client: :class:`swaggerpy.client.SwaggerClient` or :class:`bravado.client.SwaggerClient`.
    :param client_identifier: the name of the service that is using this
            generated clientlib
    :type client_identifier: string
    :param smartstack_namespace: the smartstack name of the paasta instance
            this generated clientlib is hitting
    :type smartstack_namespace: string
    """

    def __init__(self, client: Client, client_identifier: str, smartstack_namespace: str):
        self._client = client
        self.client_identifier = client_identifier
        self.smartstack_namespace = smartstack_namespace

    def __getattr__(self, name: str) -> Client:
        return OtelResourceDecorator(
            getattr(self._client, name),
            client_identifier=self.client_identifier,
            smartstack_namespace=self.smartstack_namespace,
        )

    def __dir__(self) -> list[str]:
        return dir(self._client)  # pragma: no cover





# pragma: no cover
def get_pyramid_current_request() -> pyramid.request.Request | None:
    try:
        threadlocal = importlib.import_module("pyramid.threadlocal")
    except ImportError:
        return None

    return threadlocal.get_current_request()
