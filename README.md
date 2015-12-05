# swagger_zipkin

`swagger_zipkin` contains zipkin integration tools for instrumenting downstream
 service calls made using [bravado](http://bravado.readthedocs.org/en/latest/) or
[swagger-py](http://swagger-py.readthedocs.org/en/latest/) http clients.

It is aimed to be a standalone package, with only dependancy being
[pyramid_zipkin](https://github.com/Yelp/pyramid_zipkin).

The limitations are that the service should run on
[Pyramid framework](http://docs.pylonsproject.org/en/latest/docs/pyramid.html)
and use [pyramid_zipkin](https://github.com/Yelp/pyramid_zipkin) for zipkin
integration.

Quick Start
-----------

The decorator can be applied to any swagger-py or bravado client. The example
shows a sample usage on bravado. It assume the code is being called from within
a pyramid view.

```py
from bravado.client import SwaggerClient
from swagger_zipkin.zipkin_decorator import ZipkinClientDecorator

client = SwaggerClient.from_url("http://petstore.swagger.io/v2/swagger.json")
zipkin_wrapped_client = ZipkinClientDecorator(client)

pet = zipkin_wrapped_client.pet.getPetById(petId=42).result()
```
