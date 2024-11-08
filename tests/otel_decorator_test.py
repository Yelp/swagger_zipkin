from unittest import mock

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace.span import format_span_id
from opentelemetry.trace.span import format_trace_id

from swagger_zipkin.decorate_client import Client
from swagger_zipkin.otel_decorator import OtelClientDecorator

memory_exporter = InMemorySpanExporter()
span_processor = SimpleSpanProcessor(memory_exporter)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(span_processor)

client_identifier = "test_client"
smartstack_namespace = "smartstack_namespace"
tracer = trace.get_tracer("otel_decorator")


def create_request_options(parent_span: trace.Span, exported_span: trace.Span):
    trace_id = format_trace_id(parent_span.get_span_context().trace_id)
    span_id = format_span_id(exported_span.get_span_context().span_id)
    return {
        'headers': {
            'traceparent': f'00-{trace_id}-{span_id}-01',
            'X-B3-TraceId': format_trace_id(parent_span.get_span_context().trace_id),
            'X-B3-SpanId': format_span_id(exported_span.get_span_context().span_id),
            'X-B3-ParentSpanId': format_span_id(parent_span.get_span_context().span_id),
            'X-B3-Flags': '0',
            'X-B3-Sampled': '1',
        }
    }


def test_client_request():
    client = mock.Mock(spec=Client)
    wrapped_client = OtelClientDecorator(
        client,
        client_identifier=client_identifier, 
        smartstack_namespace=smartstack_namespace
    )

    with tracer.start_as_current_span(
        "parent_span", kind=trace.SpanKind.SERVER
    ) as parent_span:
        resource = wrapped_client.resource
        param = mock.Mock()
        resource.operation(param)

        assert len(memory_exporter.get_finished_spans()) == 1
        exported_span = memory_exporter.get_finished_spans()[0]

        client.resource.operation.assert_called_with(
            param,
            _request_options=create_request_options(parent_span, exported_span)
        )

        assert exported_span.attributes["url.path"] == ""
        assert exported_span.attributes["http.request.method"] == ""
        assert exported_span.attributes["http.route"] == ""
        assert exported_span.attributes["client.namespace"] == client_identifier
        assert exported_span.attributes["peer.service"] == smartstack_namespace
        assert exported_span.attributes["server.namespace"] == smartstack_namespace
        #assert exported_span.attributes["http.response.status_code"] == ""
