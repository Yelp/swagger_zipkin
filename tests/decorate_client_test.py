# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
import pytest

from swagger_zipkin.decorate_client import decorate_client


def test_decorate_client_non_attr():
    client = object()

    with pytest.raises(AttributeError):
        decorate_client(client, mock.Mock(), 'attr')


def test_decorate_client_non_callable():
    client = mock.Mock()
    client.attr = 1

    decorated = decorate_client(client, mock.Mock(), 'attr')
    assert client.attr == decorated
