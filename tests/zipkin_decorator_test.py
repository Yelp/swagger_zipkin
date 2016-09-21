# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import mock

from swagger_zipkin.zipkin_decorator import ZipkinClientDecorator


def create_span(trace_id, span_id, parent_span_id):
    return {
        'X-B3-TraceId': trace_id,
        'X-B3-SpanId': span_id,
        'X-B3-ParentSpanId': parent_span_id,
        'X-B3-Flags': '0',
        'X-B3-Sampled': 'true',
    }


def create_request_options(trace_id, span_id, parent_span_id):
    return {
        'headers': {
            'X-B3-TraceId': trace_id,
            'X-B3-SpanId': span_id,
            'X-B3-ParentSpanId': parent_span_id,
            'X-B3-Flags': '0',
            'X-B3-Sampled': 'true',
        }
    }


def test_client_request_option_decorator():
    trace_id = 'trace_id'
    span_id = 'span_id'

    client = mock.Mock()
    wrapped_client = ZipkinClientDecorator(client)
    param = mock.Mock()

    with mock.patch('swagger_zipkin.zipkin_decorator.create_http_headers_for_new_span', side_effect=[
        create_span(trace_id, 'span1', span_id),
        create_span(trace_id, 'span2', span_id),
    ]):
        # This line is actually very important. Every time `.resource` is called,
        # a new decorator is constructed, and we want to make sure we're testing
        # against the same decorator to prevent regressing on WEBCORE-1240.
        resource = wrapped_client.resource

        resource.operation(param)
        client.resource.operation.assert_called_with(
            param,
            _request_options=create_request_options(trace_id, 'span1', span_id)
        )

        resource.operation(param)
        client.resource.operation.assert_called_with(
            param,
            _request_options=create_request_options(trace_id, 'span2', span_id)
        )
