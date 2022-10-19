[![Travis](https://img.shields.io/github/workflow/status/Yelp/swagger_zipkin/build.yaml/master.svg)](https://github.com/Yelp/swagger_zipkin/actions/workflows/build.yaml)
[![PyPi version](https://img.shields.io/pypi/v/swagger_zipkin.svg)](https://pypi.python.org/pypi/swagger_zipkin/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/swagger_zipkin.svg)](https://pypi.python.org/pypi/swagger_zipkin/)

# swagger_zipkin

`swagger_zipkin` contains zipkin integration tools for instrumenting downstream
 service calls made using [bravado](http://bravado.readthedocs.org/en/latest/) or
[swagger-py](http://swagger-py.readthedocs.org/en/latest/) http clients.

It is aimed to be a standalone package, with only dependency being
[py_zipkin](https://github.com/Yelp/py_zipkin).

Quick Start
-----------

The decorator can be applied to any swagger-py or bravado client. The example
shows a sample usage on bravado. It assume the code is being called from within
a `py_zipkin.zipkin.zipkin_span` context manager or decorator.

```py
from bravado.client import SwaggerClient
from swagger_zipkin.zipkin_decorator import ZipkinClientDecorator

client = SwaggerClient.from_url("http://petstore.swagger.io/v2/swagger.json")
zipkin_wrapped_client = ZipkinClientDecorator(client)

pet = zipkin_wrapped_client.pet.getPetById(petId=42).result()
```
