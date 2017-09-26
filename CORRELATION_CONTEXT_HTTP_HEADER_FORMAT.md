# Correlation Context HTTP Header Format

A correlation context header is used to pass the name-value context properties for the trace. This is a companion header for the `Trace-Context`. The values should be passed along to any child requests. Note that uniqueness of the key within the `Correlation-Context` is not guaranteed. Context received from upstream service may be altered before passing it along.

# Format

## Header name

`Correlation-Context`

Multiple correlation context headers are allowed. Values can be combined in a single header according to the [rfc](https://tools.ietf.org/html/rfc7230#page-24).

## Header value

`name1=value1,name2=value2`

**Limits:**
1. Maximum number of name-value pairs: `180`.
2. Maximum number of bytes per a single name-value pair: `4096`.
3. Maximum total length of all name-value pairs: `8192`.

*See [CORRELATION_CONTEXT_HTTP_HEADER_FORMAT_RATIONALE.md#Limits] for rationale of these limits.*

## Name format

Url encoded string. Spaces should be trimmed from beginning and the end of the name. Names are case sensitive.

## Value format

All spaces should be trimmed from the beginning and the end of the value.

Value represents a url encoded string. Value is case sensitive.

**Examples**:

```
component=Frontend
component=Front%3Dend
```

# Examples of HTTP headers

```
Correlation-Context: component=Frontend, flightName=DF:28, IsAuthenticated=true
```

```
Correlation-Context: component=Frontend
Correlation-Context: flight%3DName=DF:28, ExposurePercentage=33.33
```
