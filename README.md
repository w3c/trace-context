# TraceContext Specs
Specification for tracing context propagation format.

## Goal
This specification defines formats to pass trace context information across systems. Our goal is 
to share this with the community so that various tracing and diagnostics products can operate 
together.

## Headers

Trace context represented by set of name/value pairs describing identity of every http request. As a performance optimization measure few of these pairs were promoted to a separate header. This header has fixed length and defined sequence of fields.

Libraries and platforms MUST propagate `Trace-Context` and `Trace-Context-Ext` headers to guarantee that trace will not be broken. `Correlation-Context` header is a companion header representing user-defined baggage associated with the trace. 

TODO: Add details on behavior when one of the headers cannot be parsed

* See [Trace-Context Header](trace_context/README.md)
* See [Trace-Context-Ext Header](trace_context_ext/README.md)
* See [Correlation-Context Header](correlation_context/README.md)

## Reference Implementations
TODO: add link here

## Why are we doing this?
* If this becomes popular, frameworks and other services will automatically pass trace IDs 
through for correlated requests. This would prevent traces from hitting dead ends when a request 
reaches an un-instrumented service.
* Once aligned on a header name, we can ask for a CORS exception from the W3C. This would allow 
browsers to attach trace IDs to requests and submit tracing data to a distributed tracing service.
* Loggers can reliably parse trace / span IDs and include them in logs for correlation purposes.
* Customers can use multiple tracing solutions (Zipkin + New Relic) at the same time and not have
 to worry about propagating two sets of context headers.
* Frameworks can *bless* access to the trace context even if they prevent access to underlying 
request headers, making it available by default.