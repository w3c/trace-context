# Trace Context HTTP Header Format

Date: 31/03/2017

A trace context header is used to pass trace context information across systems
for a HTTP request. Our goal is to share this with the community so that various
tracing and diagnostics products can operate together, and so that services can
pass context through them, even if they're not being traced (useful for load
balancers, etc.)

# Format

## Header name

`Trace-Context`

## Field value

`base16(<version><version_format>)`

The value will be US-ASCII encoded (which is UTF-8 compliant).

### Version

Is a 1-byte representing a uint8 value.

### Version = 0

#### Format

`<trace-id><span-id><trace-options>`

All fields are required.

#### Trace-id

Is the ID of the whole trace forest. It is represented as a 16-bytes array,
e.g., `0x4bf92f3577b34da6a3ce929d0e0e4736`. All bytes 0 is considered invalid.

Implementation may decide to completely ignore the trace-context if the trace-id
is invalid.

#### Span-id

Is the ID of the caller span (parent). It is represented as a 8-bytes array,
e.g., `0x00f067aa0ba902b7`. All bytes 0 is considered invalid.

Implementation may decide to completely ignore the trace-context if the span-id
is invalid.

#### Trace-options

Controls tracing options such as sampling, trace level etc. It is a 4-bytes
representing a 32-bit unsigned integer in little-endian order. The least
significant bit provides recommendation whether the request should be traced or
not (1 recommends the request should be traced, 0 means the caller does not make
a decision to trace and the decision might be deferred). The flags are
recommendations given by the caller rather than strict rules to follow for 3
reasons:

1.  Trust and abuse.
2.  Bug in caller
3.  Different load between caller service and callee service might force callee
    to down sample.

The behavior of other bits is currently undefined.

#### Examples of HTTP headers

*Valid sampled Trace-Context:*

```
Value = 004bf92f3577b34da6a3ce929d0e0e473600f067aa0ba902b701000000
Version = 0 (0x00)
TraceId = 0x4bf92f3577b34da6a3ce929d0e0e4736
SpanId = 0x00f067aa0ba902b7
TraceOptions = 0x1  // sampled
```

*Valid not-sampled Trace-Context:*

```
Value = 004bf92f3577b34da6a3ce929d0e0e473600f067aa0ba902b700000000
Version = 0 (0x00)
TraceId = 0x4bf92f3577b34da6a3ce929d0e0e4736
SpanId = 0x00f067aa0ba902b7
TraceOptions = 0x0  // not-sampled
```
