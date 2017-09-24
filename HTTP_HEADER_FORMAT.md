# Trace Context HTTP Header Format

A trace context header is used to pass trace context information across systems
for a HTTP request. Our goal is to share this with the community so that various
tracing and diagnostics products can operate together, and so that services can
pass context through them, even if they're not being traced (useful for load
balancers, etc.)

# Format

## Header name

`Trace-Context`

## Field value

`base16(<version>)-<version_format>`

The value will be US-ASCII encoded (which is UTF-8 compliant). Character `-` is
used as a delimiter between fields.

### Version

Is a 1-byte representing a 8-bit unsigned integer. Version 255 reserved.

### Version = 0

#### Format

`base16(<trace-id>)-base16(<span-id>)-base16(<trace-options>)`

All fields are required. Character `-` is used as a delimiter between fields.

#### `trace-id`

The `trace-id` represents the ID of the whole trace tree. It is represented as a sequence of one or more
base-16 (i.e., hex-encoded) bytes. For example,
`4bf92f3577b34da6a3ce929d0e0e4736`, `a3ce929d0e0e4736`, and `01` are all valid
trace-ids. An all-zeroes value is considered invalid.

Implementation may decide to completely ignore the trace-context if the
`trace-id` is invalid.

#### `span-id`

The `span-id` represents the ID of the caller span ("parent"). It is
represented as a sequence of one or more base-16 (i.e., hex-encoded) bytes
(i.e., precisely the same format as `trace-id`, including the definition of an
invalid id).

Implementation may decide to completely ignore the trace-context if the
`span-id` is invalid.

#### `trace-options`

Controls tracing options such as sampling, trace level etc. It is a 1-byte
representing a 8-bit unsigned integer. The least significant bit provides
recommendation whether the request should be traced or not (1 recommends the
request should be traced, 0 means the caller does not make a decision to trace
and the decision might be deferred). The flags are recommendations given by the
caller rather than strict rules to follow for 3 reasons:

1.  Trust and abuse.
2.  Bug in caller
3.  Different load between caller service and callee service might force callee
    to down sample.

The behavior of other bits is currently undefined.

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

### Version = 01

#### Format

`base16(<trace-id>)-base16(<span-id>)-base2(<sampled-bit>)-base64(<baggage-json>)`

All fields are required. Character `-` is used as a delimiter between fields.

#### `trace-id`

The `trace-id` represents the ID of the whole trace tree. It is represented as a sequence of one or more
base-16 (i.e., hex-encoded) bytes. For example,
`4bf92f3577b34da6a3ce929d0e0e4736`, `a3ce929d0e0e4736`, and `01` are all valid
trace-ids. An all-zeroes value is considered invalid.

Implementation may decide to completely ignore the trace-context if the
`trace-id` is invalid.

#### `span-id`

The `span-id` represents the ID of the caller span ("parent"). It is
represented as a sequence of one or more base-16 (i.e., hex-encoded) bytes
(i.e., precisely the same format as `trace-id`, including the definition of an
invalid id).

Implementation may decide to completely ignore the trace-context if the
`span-id` is invalid.

#### `sampled-bit`

The sampled bit provides recommendation whether the request should be traced or
not (1 recommends the request should be traced, 0 means the caller does not
make a decision to trace and the decision might be deferred).

#### `baggage-json`

In order to support Tracer-specific features (richer sampling support, resource
accounting, security credentials, et cetera), "baggage" (a la PivotTracing or
the simpler [OpenTracing
variant](https://github.com/opentracing/specification/blob/master/specification.md#set-a-baggage-item))
may be present for any trace context. In `Version 1`, the key:value baggage
pairs are encoded as JSON, then further base64-encoded to play nice with the
character restrictions in HTTP headers. (As a side-note, observe that [the
base64 format](https://en.wikipedia.org/wiki/Base64#Base64_table) does not make
use of the `-` character used as a separator for the trace context).

#### Examples of well-formed HTTP headers

*Valid sampled Trace-Context:*

```
Value = 01-a3ce929d0e0e4736-00f067aa0ba902b7-1-eydsaWZlJzo0Mn0K
base16(<version>) = 01
base16(<trace-id>) = a3ce929d0e0e4736
base16(<span-id>) = 00f067aa0ba902b7
base2(<sampled-bit>) = 1
base64(<baggage-json>) = eydsaWZlJzo0Mn0K _(decodes as `{'life':42}`)_
```

*Valid not-sampled Trace-Context:*

```
Value = 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00
base16(<version>) = 00
base16(<trace-id>) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(<span-id>) = 00f067aa0ba902b7
base2(<sampled-bit>) = 0
```
