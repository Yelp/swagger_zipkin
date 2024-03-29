from __future__ import annotations

import functools
from typing import Callable
from typing import Generic
from typing import TypeVar

from typing_extensions import ParamSpec
from typing_extensions import Protocol


T = TypeVar('T', covariant=True)
P = ParamSpec('P')


class Operation(Protocol):
    ...


class Resource(Protocol[P, T]):
    def __getattr__(self, name: str) -> Operation:
        ...  # pragma: no cover

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        ...  # pragma: no cover


class Client(Protocol):
    def __getattr__(self, name: str) -> Resource:
        ...  # pragma: no cover


class OperationDecorator(Generic[P, T]):
    """A helper to preserve attributes of :class:`swaggerpy.client.Operation`
    and :class:`bravado.client.CallableOperation` while decorating their
    __call__() methods

    :param operation: callable operation, e.g., attributes of
        :class:`swaggerpy.client.Resource` or
        :class:`bravado_core.resource.Resource`
    :type  operation: :class:`swaggerpy.client.Operation` or
        :class:`bravado.client.CallableOperation`
    :param func: a callable which accepts `*args`, `**kwargs`
    :type  func: callable
    """

    def __init__(self, operation: Resource, func: Callable[P, T]) -> None:
        self.operation = operation
        self.func = func

    def __getattr__(self, name: str) -> Operation:
        return getattr(self.operation, name)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*args, **kwargs)


def decorate_client(
    api_client: Client,
    func: Callable[P, T],
    name: str,
) -> Resource[P, T]:
    """A helper for decorating :class:`bravado.client.SwaggerClient`.
    :class:`bravado.client.SwaggerClient` can be extended by creating a class
    which wraps all calls to it. This helper is used in a :func:`__getattr__`
    to check if the attr exists on the api_client. If the attr does not exist
    raise :class:`AttributeError`, if it exists and is not callable return it,
    and if it is callable return a partial function calling `func` with `name`.

    Example usage:

    .. code-block:: python

        class SomeClientDecorator(object):

            def __init__(self, api_client, ...):
                self.api_client = api_client

            # First arg should be suffiently unique to not conflict with any of
            # the kwargs
            def wrap_call(self, client_call_name, *args, **kwargs):
                ...

            def __getattr__(self, name):
                return decorate_client(self.api_client, self.wrap_call, name)

    :param api_client: the client which is being decorated
    :type  api_client: :class:`bravado.client.SwaggerClient`
    :param func: a callable which accepts `name`, `*args`, `**kwargs`
    :type  func: callable
    :param name: the attribute being accessed
    :type  name: string
    :returns: the attribute from the `api_client` or a partial of `func`
    :raises: :class:`AttributeError`
    """
    client_attr = getattr(api_client, name)
    if not callable(client_attr):
        return client_attr

    return OperationDecorator(client_attr, functools.partial(func, name))
