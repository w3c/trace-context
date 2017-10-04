# Trace Context HTTP Header Format

A trace context header is used to pass trace context information across systems for a HTTP 
request. Our goal is to share this with the community so that various tracing and diagnostics 
products can operate together, and so that services can pass context through them, even if 
they're not being traced (useful for load balancers, etc.)

# Format

## Header name

`Trace-Context`

## Field value

```
base16(<version>)-<version_format>
```

The value will be US-ASCII encoded (which is UTF-8 compliant). Character `-` is
used as a delimiter between fields.

### Version

Is a 1-byte representing a 8-bit unsigned integer. Version 255 reserved.

### Version = 0

#### Format

```
base16(<trace-id>)-base16(<span-id>)[-base16(<trace-options>)]
```

`trace-id` and `span-id` are required. The `trace-options` is optional. Character `-`
 is used as a delimiter between fields.

#### Trace-id

Is the ID of the whole trace forest. It is represented as a 16-bytes array, e.g., 
`4bf92f3577b34da6a3ce929d0e0e4736`. All bytes 0 is considered invalid.

Implementation may decide to completely ignore the trace-context if the trace-id is invalid.

#### Span-id

Is the ID of the caller span (parent). It is represented as a 8-bytes array, e.g., 
`00f067aa0ba902b7`. All bytes 0 is considered invalid.

Implementation may decide to completely ignore the trace-context if the span-id is invalid.

#### Trace-options

Controls tracing options such as sampling, trace level etc. It is a 1-byte representing a 8-bit 
unsigned integer. The flags are recommendations given by the caller rather than strict rules to 
follow for 3 reasons:

1. Trust and abuse.
2. Bug in caller
3. Different load between caller service and callee service might force callee to down sample.    

##### Bits behavior definition (01234567):
* The least significant bit (the 7th bit) provides recommendation whether the request should be 
traced or not (`1` recommends the request should be traced, `0` means the caller does not
make a decision to trace and the decision might be deferred). When `trace-options` is missing
the default value for this bit is `0`
* The behavior of other bits is currently undefined.

#### Examples of HTTP headers

*Valid sampled Trace-Context:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
base16(<Version>) = 00
base16(<TraceId>) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(<SpanId>) = 00f067aa0ba902b7
base16(<TraceOptions>) = 01  // sampled
```

*Valid not-sampled Trace-Context:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00
base16(<Version>) = 00
base16(<TraceId>) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(<SpanId>) = 00f067aa0ba902b7
base16(<TraceOptions>) = 00  // not-sampled
```
