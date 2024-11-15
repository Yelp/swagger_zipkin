from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from typing import TypeVar

from bravado.client import construct_request
from bravado.exception import HTTPError
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.span import format_span_id
from opentelemetry.trace.span import format_trace_id
from opentelemetry.trace.span import TraceFlags
from typing_extensions import ParamSpec

from swagger_zipkin.decorate_client import Client
from swagger_zipkin.decorate_client import decorate_client
from swagger_zipkin.decorate_client import Resource

T = TypeVar('T', covariant=True)
P = ParamSpec('P')

tracer = trace.get_tracer("otel_decorator")


class OtelResourceDecorator:
    """A wrapper to the swagger resource.

    :param resource: A resource object. eg. `client.pet`, `client.store`.
    :type resource: :class:`swaggerpy.client.Resource` or :class:`bravado_core.resource.Resource`
    """

    def __init__(self, resource: Resource, client_identifier: str, smartstack_namespace: str) -> None:
        self.resource = resource
        self.client_identifier = client_identifier
        self.smartstack_namespace = smartstack_namespace

    def __getattr__(self, name: str) -> Resource:
        return decorate_client(self.resource, self.with_headers, name)

    def with_headers(self, call_name: str, *args: Any, **kwargs: Any) -> Any:

        with self.handle_exception():
            kwargs.setdefault('_request_options', {})
            request_options: dict = kwargs['_request_options']
            request_options.setdefault('headers', {})

            operation = getattr(self.resource, call_name)
            request = construct_request(operation, request_options, **kwargs)  # type: ignore
            
            url = getattr(request, "url", "")
            path = getattr(request, "path", "")
            method = getattr(request, "method", "")

            parent_span = trace.get_current_span()
            span_name = f"{method} {path}"

            with tracer.start_as_current_span(
                span_name, kind=trace.SpanKind.CLIENT
            ) as span:
                span.set_attribute("url.path", url)
                span.set_attribute("http.request.method", method)
                span.set_attribute("client.namespace", self.client_identifier)
                span.set_attribute("peer.service", self.smartstack_namespace)
                span.set_attribute("server.namespace", self.smartstack_namespace)
                span.set_attribute("http.response.status_code", "200")

                self.inject_otel_headers(kwargs, span)
                self.inject_zipkin_headers(kwargs, span, parent_span)

                try:
                    operation(*args, **kwargs)
                except HTTPError as e:
                    span.set_attribute("error.type", e.__class__.__name__)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, e.message))
                    span.set_attribute("http.response.status_code", e.status_code)
                    raise e

                return operation

    @contextmanager
    def handle_exception(
        self,
    ) -> Any:
        try:
            yield
        except Exception as e:
            # not raising an exception if the instrumentation had a problem 
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
    """A wrapper to swagger client (swagger-py or bravado) to pass on otel and zipkin
    headers to the service call. It will also generate a CLIENT span for the outgoing call.

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
