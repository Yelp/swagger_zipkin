from unittest import mock

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


def test_decorate_client_callable_being_invoked():
    def foo(a, b, c):
        pass

    client = mock.Mock()
    client.attr = foo
    decorated_foo = mock.Mock()

    decorated_callable = decorate_client(client, decorated_foo, 'attr')
    assert decorated_callable.operation == foo

    # Ensure that it's `decorated_foo` being called, not `foo`
    decorated_callable()
    decorated_foo.assert_called_once_with('attr')


def test_decorate_client_callable_attribute_retrieved():
    class Foo:
        def __init__(self):
            self.bar = 'bar'

        def __call__(self, a, b, c):
            return a + b + c

    client = mock.Mock()
    client.attr = Foo()
    decorated_foo = mock.Mock(return_value=100)
    decorated_callable = decorate_client(client, decorated_foo, 'attr')

    # `decorated_foo` is called, not `Foo().__call__`
    assert decorated_callable(2, 3, 7) == 100
    # Foo().bar is accessible after it is decorated
    assert decorated_callable.bar == 'bar'
