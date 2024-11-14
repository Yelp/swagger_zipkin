from unittest import mock

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace.span import format_span_id
from opentelemetry.trace.span import format_trace_id

from swagger_zipkin.otel_decorator import OtelClientDecorator
from swagger_zipkin.otel_decorator import OtelResourceDecorator

memory_exporter = InMemorySpanExporter()
span_processor = SimpleSpanProcessor(memory_exporter)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(span_processor)

client_identifier = "test_client"
smartstack_namespace = "smartstack_namespace"
tracer = trace.get_tracer("otel_decorator")


@pytest.fixture
def setup():
    memory_exporter.clear()


@pytest.fixture
def get_request():
    mock_request = mock.Mock()
    mock_request.path = "/sample-url"
    mock_request.method = "GET"
    mock_request.matched_route = "sample-view"
    return mock_request


def create_request_options(parent_span: trace.Span, exported_span: trace.Span):
    trace_id = format_trace_id(exported_span.get_span_context().trace_id)
    span_id = format_span_id(exported_span.get_span_context().span_id)

    headers = {}
    headers['headers'] = {
        'traceparent': f'00-{trace_id}-{span_id}-01',
        'X-B3-TraceId': trace_id,
        'X-B3-SpanId': span_id,
        'X-B3-Flags': '0',
        'X-B3-Sampled': '1',
    }
    if parent_span is not None:
        headers['headers']['X-B3-ParentSpanId'] = format_span_id(parent_span.get_span_context().span_id)
    
    return headers


@mock.patch(
    "swagger_zipkin.otel_decorator.get_pyramid_current_request", autospec=True
)
def test_client_request(mock_request, get_request, setup):
    mock_request.return_value = get_request

    with tracer.start_as_current_span(
        "parent_span", kind=trace.SpanKind.SERVER
    ) as parent_span:
        client = mock.Mock()
        wrapped_client = OtelClientDecorator(
            client,
            client_identifier=client_identifier,
            smartstack_namespace=smartstack_namespace
        )
        resource = wrapped_client.resource
        param1 = mock.Mock()
        resource.operation(param1)

        assert len(memory_exporter.get_finished_spans()) == 1
        exported_span = memory_exporter.get_finished_spans()[0]

        client.resource.operation.assert_called_with(
            param1,
            _request_options=create_request_options(parent_span, exported_span)
        )

        assert exported_span.name == f"{get_request.method} {get_request.matched_route}"
        assert exported_span.attributes["url.path"] == get_request.path
        assert exported_span.attributes["http.request.method"] == get_request.method
        assert exported_span.attributes["http.route"] == get_request.matched_route
        assert exported_span.attributes["client.namespace"] == client_identifier
        assert exported_span.attributes["peer.service"] == smartstack_namespace
        assert exported_span.attributes["server.namespace"] == smartstack_namespace
        assert exported_span.attributes["http.response.status_code"] == "200"

        param2 = mock.Mock()
        resource.operation(param2)

        assert len(memory_exporter.get_finished_spans()) == 2
        exported_span = memory_exporter.get_finished_spans()[1]

        client.resource.operation.assert_called_with(
            param2,
            _request_options=create_request_options(parent_span, exported_span)
        )

        assert exported_span.name == f"{get_request.method} {get_request.matched_route}"
        assert exported_span.attributes["url.path"] == get_request.path
        assert exported_span.attributes["http.request.method"] == get_request.method
        assert exported_span.attributes["http.route"] == get_request.matched_route
        assert exported_span.attributes["client.namespace"] == client_identifier
        assert exported_span.attributes["peer.service"] == smartstack_namespace
        assert exported_span.attributes["server.namespace"] == smartstack_namespace
        assert exported_span.attributes["http.response.status_code"] == "200"




@mock.patch(
    "swagger_zipkin.otel_decorator.get_pyramid_current_request", autospec=True
)
def test_client_request_no_parent_span(mock_request, get_request, setup):
    mock_request.return_value = get_request

    client = mock.Mock()
    wrapped_client = OtelClientDecorator(
        client,
        client_identifier=client_identifier,
        smartstack_namespace=smartstack_namespace
    )
    resource = wrapped_client.resource
    param = mock.Mock()
    resource.operation(param)

    assert len(memory_exporter.get_finished_spans()) == 1
    exported_span = memory_exporter.get_finished_spans()[0]

    client.resource.operation.assert_called_with(
        param,
        _request_options=create_request_options(None, exported_span)
    )

    assert exported_span.name == f"{get_request.method} {get_request.matched_route}"
    assert exported_span.attributes["url.path"] == get_request.path
    assert exported_span.attributes["http.request.method"] == get_request.method
    assert exported_span.attributes["http.route"] == get_request.matched_route
    assert exported_span.attributes["client.namespace"] == client_identifier
    assert exported_span.attributes["peer.service"] == smartstack_namespace
    assert exported_span.attributes["server.namespace"] == smartstack_namespace
    assert exported_span.attributes["http.response.status_code"] == "200"


@mock.patch(
    "swagger_zipkin.otel_decorator.get_pyramid_current_request", autospec=True
)
def test_with_headers_exception(mock_request, get_request, setup):
    mock_request.return_value = get_request

    # Create a mock resource and configure it to raise an exception
    mock_resource = mock.MagicMock()
    mock_method = mock.MagicMock(side_effect=Exception("simulated exception"))
    setattr(mock_resource, 'test_operation', mock_method)

    decorator = OtelResourceDecorator(resource=mock_resource, client_identifier="test_client",
                                      smartstack_namespace="smartstack_namespace")

    # Prepare arguments
    args = ()
    kwargs = {'_request_options': {'headers': {}}}

    with pytest.raises(Exception):
        decorator.with_headers("test_operation", *args, **kwargs)

    assert len(memory_exporter.get_finished_spans()) == 1
    exported_span = memory_exporter.get_finished_spans()[0]

    expected_headers = kwargs['_request_options']['headers']
    actual_headers = create_request_options(None, exported_span)['headers']
    assert expected_headers == actual_headers

    assert exported_span.name == f"{get_request.method} {get_request.matched_route}"
    assert exported_span.attributes["url.path"] == get_request.path
    assert exported_span.attributes["http.request.method"] == get_request.method
    assert exported_span.attributes["http.route"] == get_request.matched_route
    assert exported_span.attributes["client.namespace"] == client_identifier
    assert exported_span.attributes["peer.service"] == smartstack_namespace
    assert exported_span.attributes["server.namespace"] == smartstack_namespace
    assert exported_span.attributes["error.type"] == "Exception" 
    assert exported_span.attributes["http.response.status_code"] == "500"
