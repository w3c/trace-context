# Request Context HTTP Header Format

A request context header is used to pass the name-value request properties to the next component or return them to caller. The values should be passed along to child requests by proxies. However it should not be passed by any tracing library. The format of the header is exactly the same as a `Correlation-Context` header format.

*See [rationale document](HTTP_HEADER_FORMAT_RATIONALE.md) for details of decisions made for this format.*
*See [Correlation-Context specification](../correlation_context/HTTP_HEADER_FORMAT.md) for details of decisions made for this format.*

# Format

## Header name

`Request-Context`

Multiple correlation context headers are allowed. Values can be combined in a single header according to the [RFC 7230](https://tools.ietf.org/html/rfc7230#page-24).

## Header value

See [Correlation-Context specification](../correlation_context/HTTP_HEADER_FORMAT.md)

