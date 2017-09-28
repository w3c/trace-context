# TraceContext Specs
Specification for TraceContext propagation format.

## Goal
This specification defines formats to pass trace context information across systems. Our goal is to share this with the community so that various tracing and diagnostics products can operate together, and so that services can pass context through them, even if they're not being traced (useful for load balancers, etc.).

## HTTP Format
The HTTP format is defined [here](HTTP_HEADER_FORMAT.md)

## Binary Format
TODO: add link here

## Reference Implementations
TODO: add link here

## Why are we doing this?
* If this becomes popular, frameworks and other services will automatically pass trace IDs through for correlated requests. This would prevent traces from hitting dead ends when a request reaches an un-instrumented service.
* Once aligned on a header name, we can ask for a CORS exception from the W3C. This would allow browsers to attach trace IDs to requests and submit tracing data to a distributed tracing service.
* Loggers can reliably parse trace / span IDs and include them in logs for correlation purposes.
* Customers can use multiple tracing solutions (Zipkin + New Relic) at the same time and not have to worry about propagating two sets of context headers.
* Frameworks can *bless* access to the trace context even if they prevent access to underlying request headers, making it available by default.
